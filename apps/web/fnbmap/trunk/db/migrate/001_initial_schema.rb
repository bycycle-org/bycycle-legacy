class CreateEventsAndLocations < ActiveRecord::Migration
  def self.up
    create_table :events do |t|
      t.column :name, :string
      t.column :location_id, :integer
      t.column :day_id, :integer
      t.column :start_time, :time
    end
    
    create_table :locations do |t|
      t.column :name, :string    
      t.column :description, :text
      t.column :latitude, :double
      t.column :longitude, :double      
      t.column :address, :string
      t.column :city, :string
      t.column :state, :string, :limit => 2
      t.column :zip, :integer
    end
    
    create_table :days do |t|
      t.column :name, :string
    end
  end

  def self.down
    drop_table :events
    drop_table :locations
    drop_table :days
  end
end
