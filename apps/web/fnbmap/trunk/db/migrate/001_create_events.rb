class CreateEvents < ActiveRecord::Migration
  def self.up
    create_table :events do |t|
      t.column :name, :string
      t.column :location_id, :integer
      t.column :day_id, :integer
      t.column :start_time, :time
    end
  end

  def self.down
    drop_table :events
  end
end
