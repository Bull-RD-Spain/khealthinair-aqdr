-- Copyright © 2021-2026 Bull SAS
-- SPDX-License-Identifier: GPL-3.0-or-later
--
-- This file is part of work done in the K-HEALTHinAIR EU funded project.
--
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
--
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with this program.  If not, see <https://www.gnu.org/licenses/>.

--CREATE DATABASE "sensors"; -- Created in aqdr-platform-db docker img POSTGRES_DB env variable as initial DB

ALTER database template0 is_template false;
ALTER database template1 is_template false;
DROP DATABASE template0;
DROP DATABASE template1;
DROP DATABASE postgres;

ALTER DATABASE "sensors" OWNER TO "sensors";
GRANT ALL PRIVILEGES ON DATABASE "sensors" TO "sensors";

\connect "sensors" khealthinair_admin
GRANT CONNECT ON DATABASE "sensors" TO "sensors";
GRANT ALL ON SCHEMA public TO "sensors";
GRANT ALL ON ALL TABLES IN SCHEMA public TO "sensors";

\connect "sensors" "sensors"
CREATE TABLE "public"."sensors" (
    "sensor_id" character varying(50) PRIMARY KEY,
    "apikey" character varying(100) NOT NULL,
    "provider" character varying(2) NOT NULL,
    "pilot" character varying(2) NOT NULL,
    "scenario" character varying(5) NOT NULL,
    "area" integer NOT NULL,
    "outdoor_apikey" character varying(100) NOT NULL,
    "building" integer NOT NULL,
    "inclusion_time" timestamp
) WITH (oids = false);
COMMENT ON TABLE "public"."sensors" IS 'Table for sensors maintenance';
COMMENT ON COLUMN "public"."sensors"."sensor_id" IS 'Sensor identifier';
COMMENT ON COLUMN "public"."sensors"."apikey" IS 'API Key associated with specific sensor_id for indoor data';
COMMENT ON COLUMN "public"."sensors"."provider" IS 'Type of the sensor (IB: inBiot, MH: Mann+Hummel)';
COMMENT ON COLUMN "public"."sensors"."pilot" IS 'Pilot location of the sensor device: AT, ES, DE, NL, NO, PL';
COMMENT ON COLUMN "public"."sensors"."scenario" IS 'Scenario location of the sensor (3-letter + 2-digit code).';
COMMENT ON COLUMN "public"."sensors"."area" IS 'Area location of the sensor';
COMMENT ON COLUMN "public"."sensors"."outdoor_apikey" IS 'API Key associated with specific building for outdoor data';
COMMENT ON COLUMN "public"."sensors"."building" IS 'Building ID for Outdoor Air Quality';
COMMENT ON COLUMN "public"."sensors"."inclusion_time" IS 'Date when the sensor device details where included';
