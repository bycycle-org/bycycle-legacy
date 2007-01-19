require File.dirname(__FILE__) + '/../test_helper'
require 'days_controller'

# Re-raise errors caught by the controller.
class DaysController; def rescue_action(e) raise e end; end

class DaysControllerTest < Test::Unit::TestCase
  fixtures :days

  def setup
    @controller = DaysController.new
    @request    = ActionController::TestRequest.new
    @response   = ActionController::TestResponse.new
  end

  def test_index
    get :index
    assert_response :success
    assert_template 'list'
  end

  def test_list
    get :list

    assert_response :success
    assert_template 'list'

    assert_not_nil assigns(:days)
  end

  def test_show
    get :show, :id => 1

    assert_response :success
    assert_template 'show'

    assert_not_nil assigns(:day)
    assert assigns(:day).valid?
  end

  def test_new
    get :new

    assert_response :success
    assert_template 'new'

    assert_not_nil assigns(:day)
  end

  def test_create
    num_days = Day.count

    post :create, :day => {}

    assert_response :redirect
    assert_redirected_to :action => 'list'

    assert_equal num_days + 1, Day.count
  end

  def test_edit
    get :edit, :id => 1

    assert_response :success
    assert_template 'edit'

    assert_not_nil assigns(:day)
    assert assigns(:day).valid?
  end

  def test_update
    post :update, :id => 1
    assert_response :redirect
    assert_redirected_to :action => 'show', :id => 1
  end

  def test_destroy
    assert_not_nil Day.find(1)

    post :destroy, :id => 1
    assert_response :redirect
    assert_redirected_to :action => 'list'

    assert_raise(ActiveRecord::RecordNotFound) {
      Day.find(1)
    }
  end
end
