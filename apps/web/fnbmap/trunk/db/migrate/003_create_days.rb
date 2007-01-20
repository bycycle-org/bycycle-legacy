require 'date'

class CreateDays < ActiveRecord::Migration
  def self.up
    create_table :days do |t|
      t.column :name, :string
    end
    days = %w[mon tues wednes thurs fri satur sun]
    days.each() do |day|
      Day.create :name => day + 'day'
    end
  end

  def self.down
    drop_table :days
  end
end
