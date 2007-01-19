class Location < ActiveRecord::Base
  has_many :events
  validates_presence_of :latitude
  validates_numericality_of :latitude
  validates_presence_of :longitude
  validates_numericality_of :longitude
  #validates_numericality_of :zip
  #validates_length_of :state, :is => 2
end
