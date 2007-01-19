require File.dirname(__FILE__) + '/../test_helper'

class EventTest < Test::Unit::TestCase
  fixtures :events

	NEW_EVENT = {}	# e.g. {:name => 'Test Event', :description => 'Dummy'}
	REQ_ATTR_NAMES 			 = %w( ) # name of fields that must be present, e.g. %(name description)
	DUPLICATE_ATTR_NAMES = %w( ) # name of fields that cannot be a duplicate, e.g. %(name description)

  def setup
    # Retrieve fixtures via their name
    # @first = events(:first)
  end

  def test_raw_validation
    event = Event.new
    if REQ_ATTR_NAMES.blank?
      assert event.valid?, "Event should be valid without initialisation parameters"
    else
      # If Event has validation, then use the following:
      assert !event.valid?, "Event should not be valid without initialisation parameters"
      REQ_ATTR_NAMES.each {|attr_name| assert event.errors.invalid?(attr_name.to_sym), "Should be an error message for :#{attr_name}"}
    end
  end

	def test_new
    event = Event.new(NEW_EVENT)
    assert event.valid?, "Event should be valid"
   	NEW_EVENT.each do |attr_name|
      assert_equal NEW_EVENT[attr_name], event.attributes[attr_name], "Event.@#{attr_name.to_s} incorrect"
    end
 	end

	def test_validates_presence_of
   	REQ_ATTR_NAMES.each do |attr_name|
			tmp_event = NEW_EVENT.clone
			tmp_event.delete attr_name.to_sym
			event = Event.new(tmp_event)
			assert !event.valid?, "Event should be invalid, as @#{attr_name} is invalid"
    	assert event.errors.invalid?(attr_name.to_sym), "Should be an error message for :#{attr_name}"
    end
 	end

	def test_duplicate
    current_event = Event.find_first
   	DUPLICATE_ATTR_NAMES.each do |attr_name|
   		event = Event.new(NEW_EVENT.merge(attr_name.to_sym => current_event[attr_name]))
			assert !event.valid?, "Event should be invalid, as @#{attr_name} is a duplicate"
    	assert event.errors.invalid?(attr_name.to_sym), "Should be an error message for :#{attr_name}"
		end
	end
end

