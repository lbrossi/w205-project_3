create external table if not exists default.purchase_weapon ( 
    raw_event string,
    Host string, 
    timestamp string,
    event_type string,
    weapon_type string,
    damage_level int,
    range int,
    gold_cost int
    ) 
    stored as parquet
    location '/tmp/purchase_weapon'
    tblproperties ("parquet.compress"="SNAPPY");
    
create external table if not exists default.join_guild ( 
    raw_event string,
    Host string, 
    timestamp string,
    event_type string,
    guild_name string,
    special_power string
    ) 
    stored as parquet
    location '/tmp/join_guild'
    tblproperties ("parquet.compress"="SNAPPY");
    
create external table if not exists default.enter_battle ( 
    raw_event string,
    Host string, 
    timestamp string,
    event_type string,
    enemy string,
    outcome string
    ) 
    stored as parquet
    location '/tmp/enter_battle'
    tblproperties ("parquet.compress"="SNAPPY");