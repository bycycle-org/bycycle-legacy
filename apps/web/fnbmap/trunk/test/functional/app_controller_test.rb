require File.dirname(__FILE__) + '/../test_helper'
require 'app_controller'

# Re-raise errors caught by the controller.
class AppController; def rescue_action(e) raise e end; end

class AppControllerTest < Test::Unit::TestCase
  def setup
    @controller = AppController.new
    @request    = ActionController::TestRequest.new
    @response   = ActionController::TestResponse.new
  end

  # Replace this with your real tests.
  def test_truth
    assert true
  end
end
