#A hash of compiled regular expressions corresponding to different
#types of address or address portions. Defined regexen include
#type, number, fraction, state, direct(ion), dircode, zip, corner,
#street, place, address, and intersection.

our %Addr_Match = (
    type    => join("|", keys %_Street_Type_List),
    number  => qr/\d+-?\d*/,
    fraction => qr{\d+\/\d+},
    state   => join("|", %State_Code),
    direct  => join("|",
                    # map direction names to direction codes
                    keys %Directional,
                    # also map the dotted version of the code to the code itself
                    map { my $c = $_;
                          $c =~ s/(\w)/$1./g;
                          ( quotemeta $c, $_ ) }
                    sort { length $b <=> length $a }
                    values %Directional),
    dircode => join("|", keys %Direction_Code), 
    zip     => qr/\d{5}(?:-\d{4})?/,
    corner  => qr/(?:\band\b|\bat\b|&|\@)/i,
    unit    => qr/(?:(?:su?i?te|p\W*[om]\W*b(?:ox)?|dept|apt|ro*m|fl|apt|unit|box)\W+|#\W*)[\w-]+/i,
);

{
    use re 'eval';
    $Addr_Match{street} = qr/
        (?:
          # special case for addresses like 100 South Street
          (?:($Addr_Match{direct})\W+           (?{ $_{street} = $^N })
             ($Addr_Match{type})\b              (?{ $_{type}   = $^N }))
          |
          (?:($Addr_Match{direct})\W+           (?{ $_{prefix} = $^N }))?
          (?:
            ([^,]+)                             (?{ $_{street} = $^N })
            (?:[^\w,]+($Addr_Match{type})\b     (?{ $_{type}   = $^N }))
            (?:[^\w,]+($Addr_Match{direct})\b   (?{ $_{suffix} = $^N }))?
           |
            ([^,]*\d)                           (?{ $_{street} = $^N })
            ($Addr_Match{direct})\b             (?{ $_{suffix} = $^N })
           |
            ([^,]+?)                            (?{ $_{street} = $^N })
            (?:[^\w,]+($Addr_Match{type})\b     (?{ $_{type}   = $^N }))?
            (?:[^\w,]+($Addr_Match{direct})\b   (?{ $_{suffix} = $^N }))?
          )
        )
        /ix;

    $Addr_Match{place} = qr/
        (?:
            ([^\d,]+?)\W+                       (?{ $_{city}   = $^N })
            ($Addr_Match{state})\W*             (?{ $_{state}  = $^N })
        )?
        (?:($Addr_Match{zip})                   (?{ $_{zip}    = $^N }))?
        /ix;

    $Addr_Match{address} = qr/^\W*
        (  $Addr_Match{number})\W*              (?{ $_{number} = $^N })
        (?:$Addr_Match{fraction}\W*)?
           $Addr_Match{street}\W+
        (?:$Addr_Match{unit}\W+)?
           $Addr_Match{place}
        \W*$/ix;

    $Addr_Match{intersection} = qr/^\W*
           $Addr_Match{street}\W*?      
            (?{ @_{qw{prefix1 street1 type1 suffix1}}
                = delete @_{qw{prefix street type suffix }} })

        \s+$Addr_Match{corner}\s+

           $Addr_Match{street}\W+
            (?{ @_{qw{prefix2 street2 type2 suffix2}}
                = delete @_{qw{prefix street type suffix }} })

           $Addr_Match{place}
        \W*$/ix;
}

our %Normalize_Map = (
    prefix  => \%Directional,
    prefix1 => \%Directional,
    prefix2 => \%Directional,
    suffix  => \%Directional,
    suffix1 => \%Directional,
    suffix2 => \%Directional,
    type    => \%Street_Type,
    type1   => \%Street_Type,
    type2   => \%Street_Type,
    state   => \%State_Code,
);

=back

=head1 CLASS METHODS

=item Geo::StreetAddress::US->parse_location( $string )

Parses any address or intersection string and returns the appropriate
specifier, by calling parse_intersection() or parse_address() as needed.

=cut

sub parse_location {
    my ($class, $addr) = @_;
    if ($addr =~ /$Addr_Match{corner}/ios) {
        $class->parse_intersection($addr);
    } else {
        $class->parse_address($addr);
    }
}

=item Geo::StreetAddress::US->parse_address( $address_string )

Parses a street address into an address specifier, returning undef if
the address cannot be parsed. You probably want to use parse_location()
instead.

=cut

sub parse_address {
    my ($class, $addr) = @_;
    local %_;

    if ($addr =~ /$Addr_Match{address}/ios) {
        my %part = %_;
        ### the next line is just to make fossil tests work
        $part{$_} ||= undef for qw{prefix type suffix city state zip};
        return $class->normalize_address(\%part);
    }
}

=item Geo::StreetAddress::US->parse_intersection( $intersection_string )

Parses an intersection string into an intersection specifier, returning
undef if the address cannot be parsed. You probably want to use
parse_location() instead.

=cut

sub parse_intersection {
    my ($class, $addr) = @_;
    local %_;

    if ($addr =~ /$Addr_Match{intersection}/ios) {
        my %part = %_;
        ### the next line is just to make fossil tests work
        $part{$_} ||= undef 
            for qw{prefix1 type1 suffix1 prefix2 type2 suffix2 city state zip};

        if ( $part{type2} and $part{type2} =~ s/s\W*$//ios ) {
            if ( $part{type2} =~ /^$Addr_Match{type}$/ios && ! $part{type1} ) {
                $part{type1} = $part{type2};
            } else {
                $part{type2} .= "s";
            }
        }

        return $class->normalize_address(\%part);
    }
}

=item Geo::StreetAddress::US->normalize_address( $spec )

Takes an address or intersection specifier, and normalizes its components,
stripping out all leading and trailing whitespace and punctuation, and
substituting official abbreviations for prefix, suffix, type, and state values.
Also, city names that are prefixed with a directional abbreviation (e.g. N, NE,
etc.) have the abbreviation expanded.  The normalized specifier is returned.

Typically, you won't need to use this method, as the C<parse_*()> methods
call it for you.

N.B., C<normalize_address()> crops 9-digit ZIP codes to 5 digits. This is for
the benefit of Geo::Coder::US and may not be what you want. E-mail me if this
is a problem and I'll see what I can do to fix it.

=cut

sub normalize_address {
    my ($class, $part) = @_;
    
    # strip off punctuation
    defined($_) && s/^\s+|\s+$|[^\w\s\-]//gos for values %$part;

    while (my ($key, $map) = each %Normalize_Map) {
        $part->{$key} = $map->{lc $part->{$key}}
              if  exists $part->{$key}
              and exists $map->{lc $part->{$key}};
    }

    $part->{$_} = ucfirst lc $part->{$_} 
        for grep(exists $part->{$_}, qw( type type1 type2 ));

    # attempt to expand directional prefixes on place names
    $part->{city} =~ s/^($Addr_Match{dircode})\s+(?=\S)
                      /\u$Direction_Code{$1} /iosx
                      if $part->{city};

    # strip ZIP+4
    $part->{zip} =~ s/-.*$//os if $part->{zip};

    return $part;
}
