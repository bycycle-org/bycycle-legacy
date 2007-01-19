require File.dirname(__FILE__) + '/../test_helper'
require 'events_controller'

# Re-raise errors caught by the controller.
class EventsController; def rescue_action(e) raise e end; end

class EventsControllerTest < Test::Unit::TestCase
  fixtures :events

	NEW_EVENT = {}	# e.g. {:name => 'Test Event', :description => 'Dummy'}
	REDIRECT_TO_MAIN = {:action => 'list'} # put hash or string redirection that you normally expect

	def setup
		@controller = EventsController.new
		@request    = ActionController::TestRequest.new
		@response   = ActionController::TestResponse.new
		# Retrieve fixtures via their name
		# @first = events(:first)
		@first = Event.find_first
	end

  def test_component
    get :component
    assert_response :success
    assert_template 'events/component'
    events = check_attrs(%w(events))
    assert_equal Event.find(:all).length, events.length, "Incorrect number of events shown"
  end

  def test_component_update
    get :component_update
    assert_response :redirect
    assert_redirected_to REDIRECT_TO_MAIN
  end

  def test_component_update_xhr
    xhr :get, :component_update
    assert_response :success
    assert_template 'events/component'
    events = check_attrs(%w(events))
    assert_equal Event.find(:all).length, events.length, "Incorrect number of events shown"
  end

  def test_create
  	event_count = Event.find(:all).length
    post :create, {:event => NEW_EVENT}
    event, successful = check_attrs(%w(event successful))
    assert successful, "Should be successful"
    assert_response :redirect
    assert_redirected_to REDIRECT_TO_MAIN
    assert_equal event_count + 1, Event.find(:all).length, "Expected an additional Event"
  end

  def test_create_xhr
  	event_count = Event.find(:all).length
    xhr :post, :create, {:event => NEW_EVENT}
    event, successful = check_attrs(%w(event successful))
    assert successful, "Should be successful"
    assert_response :success
    assert_template 'create.rjs'
    assert_equal event_count + 1, Event.find(:all).length, "Expected an additional Event"
  end

  def test_update
  	event_count = Event.find(:all).length
    post :update, {:id => @first.id, :event => @first.attributes.merge(NEW_EVENT)}
    event, successful = check_attrs(%w(event successful))
    assert successful, "Should be successful"
    event.reload
   	NEW_EVENT.each do |attr_name|
      assert_equal NEW_EVENT[attr_name], event.attributes[attr_name], "@event.#{attr_name.to_s} incorrect"
    end
    assert_equal event_count, Event.find(:all).length, "Number of Events should be the same"
    assert_response :redirect
    assert_redirected_to REDIRECT_TO_MAIN
  end

  def test_update_xhr
  	event_count = Event.find(:all).length
    xhr :post, :update, {:id => @first.id, :event => @first.attributes.merge(NEW_EVENT)}
    event, successful = check_attrs(%w(event successful))
    assert successful, "Should be successful"
    event.reload
   	NEW_EVENT.each do |attr_name|
      assert_equal NEW_EVENT[attr_name], event.attributes[attr_name], "@event.#{attr_name.to_s} incorrect"
    end
    assert_equal event_count, Event.find(:all).length, "Number of Events should be the same"
    assert_response :success
    assert_template 'update.rjs'
  end

  def test_destroy
  	event_count = Event.find(:all).length
    post :destroy, {:id => @first.id}
    assert_response :redirect
    assert_equal event_count - 1, Event.find(:all).length, "Number of Events should be one less"
    assert_redirected_to REDIRECT_TO_MAIN
  end

  def test_destroy_xhr
  	event_count = Event.find(:all).length
    xhr :post, :destroy, {:id => @first.id}
    assert_response :success
    assert_equal event_count - 1, Event.find(:all).length, "Number of Events should be one less"
    assert_template 'destroy.rjs'
  end

protected
	# Could be put in a Helper library and included at top of test class
  def check_attrs(attr_list)
    attrs = []
    attr_list.each do |attr_sym|
      attr = assigns(attr_sym.to_sym)
      assert_not_nil attr,       "Attribute @#{attr_sym} should not be nil"
      assert !attr.new_record?,  "Should have saved the @#{attr_sym} obj" if attr.class == ActiveRecord
      attrs << attr
    end
    attrs.length > 1 ? attrs : attrs[0]
  end
end
