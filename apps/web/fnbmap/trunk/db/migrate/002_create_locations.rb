class CreateLocations < ActiveRecord::Migration
  def self.up
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
  end

  def self.down
    drop_table :locations
  end
end
