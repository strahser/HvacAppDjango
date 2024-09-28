INSERT INTO "StaticDB_buildingtype" ("id","name","description") VALUES (1,'1','Жилые, лечебно-профилактические и детские учреждения, школы, интернаты, гостиницы и общежития');
INSERT INTO "StaticDB_buildingtype" ("id","name","description") VALUES (2,'2','Общественные, кроме указанных выше, административные и бытовые, производственные и другие здания и помещения с влажным или мокрым режимами');
INSERT INTO "StaticDB_buildingtype" ("id","name","description") VALUES (3,'3','Производственные с сухим и нормальным режимами');

INSERT INTO "StaticDB_buildingproperty" ("id", "wall", "roof", "floor", "window", "skylight", "building_type_id",
                                         "structure_coefficient_id")
VALUES (1, 0.00035, 0.0005, 0.00045, NULL, 2.5e-05, 1, 1);
INSERT INTO "StaticDB_buildingproperty" ("id", "wall", "roof", "floor", "window", "skylight", "building_type_id",
                                         "structure_coefficient_id")
VALUES (2, 1.4, 2.2, 1.9, NULL, 0.25, 1, 2);
INSERT INTO "StaticDB_buildingproperty" ("id", "wall", "roof", "floor", "window", "skylight", "building_type_id",
                                         "structure_coefficient_id")
VALUES (3, 0.0003, 0.0004, 0.00035, 5.0e-05, 2.5e-05, 2, 1);
INSERT INTO "StaticDB_buildingproperty" ("id", "wall", "roof", "floor", "window", "skylight", "building_type_id",
                                         "structure_coefficient_id")
VALUES (4, 1.2, 1.6, 1.3, 0.2, 0.25, 2, 2);
INSERT INTO "StaticDB_buildingproperty" ("id", "wall", "roof", "floor", "window", "skylight", "building_type_id",
                                         "structure_coefficient_id")
VALUES (5, 0.0002, 0.00025, 0.0002, 2.5e-05, 2.5e-05, 3, 1);
INSERT INTO "StaticDB_buildingproperty" ("id", "wall", "roof", "floor", "window", "skylight", "building_type_id",
                                         "structure_coefficient_id")
VALUES (6, 1.0, 1.5, 1.0, 0.2, 0.15, 3, 2);

INSERT INTO "StaticDB_structurecoefficient" ("id", "name")
VALUES (1, 'a');
INSERT INTO "StaticDB_structurecoefficient" ("id", "name")
VALUES (2, 'b');

CREATE VIEW IF NOT EXISTS unique_family_devices AS
SELECT DISTINCT family_device_name
FROM Terminals_EquipmentBase;