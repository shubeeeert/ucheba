-- ===================================================================
-- 0. FIXING SPECIES CONSTRAINT (to allow English names)
-- ===================================================================
ALTER TABLE species DROP CONSTRAINT IF EXISTS chk_species_name;
ALTER TABLE species ADD CONSTRAINT chk_species_name CHECK (
    name IN ('Dog', 'Cat', 'Bird', 'Rodent', 'Reptile', 'Exotic')
);

-- ===================================================================
-- 1. REFERENCE DATA POPULATION
-- ===================================================================

-- Species (IDs: 1-Dog, 2-Cat, 3-Bird, 4-Rodent)
INSERT INTO species (name) VALUES 
('Dog'), 
('Cat'), 
('Bird'), 
('Rodent');

-- Breeds (IDs: 1..6)
INSERT INTO breed (species_id, name) VALUES 
(1, 'Welsh Corgi'),          -- 1
(1, 'German Shepherd'),      -- 2
(2, 'Maine Coon'),           -- 3
(2, 'Sphynx'),               -- 4
(3, 'Cockatiel'),            -- 5
(4, 'Guinea Pig');           -- 6

-- Symptoms (IDs: 1..6)
INSERT INTO symptom (name) VALUES 
('Vomiting'), 
('Lethargy'), 
('Loss of appetite'), 
('Itching'), 
('Lameness'), 
('Coughing');

-- Diagnoses (IDs: 1..6)
INSERT INTO diagnosis (name, icd_code) VALUES 
('Gastritis', 'K29.7'),
('Otitis', 'H66.9'),
('Babesiosis', 'B60.0'),
('Dermatitis', 'L20.9'),
('Radius fracture', 'S52.3'),
('Clinically healthy (Routine checkup)', 'Z00.0');

-- Treatments/Medications (IDs: 1..6)
INSERT INTO treatment (name) VALUES 
('Antibiotic (Synulox)'), 
('IV Fluid Therapy (Saline)'), 
('Ear flushing (Otifree)'), 
('Triderm Ointment'), 
('Vitamin Complex'), 
('Splint/Cast application');

-- Vaccines (IDs: 1..4)
INSERT INTO vaccine (name, manufacturer) VALUES 
('Nobivac DHPPi', 'MSD Animal Health'), -- 1 (Dogs)
('Nobivac Rabies', 'MSD Animal Health'),-- 2 (Rabies)
('Purevax RCP', 'Merial'),              -- 3 (Cats)
('Rabifel', 'Vetbiochim');              -- 4 (Cats)

-- ===================================================================
-- 2. OWNERS, PETS, DOCTORS
-- ===================================================================

-- Owners (5 people)
INSERT INTO owner (full_name, phone, email) VALUES 
('John Smith', '+15551234567', 'jsmith@email.com'),
('Alice Brown', '+15559876543', 'abrown@email.com'),
('David Wilson', '+15553334455', 'dwilson_88@gmail.com'),
('Emily Clark', '+15558887766', 'e.clark@yahoo.com'),
('Michael Johnson', '+15552221100', 'mjohnson@outlook.com');

-- Pets (6 animals, 4 different species)
INSERT INTO pet (owner_id, breed_id, name, birth_date) VALUES 
(1, 1, 'Rex', '2020-05-10'),      -- 1 (Smith's Corgi)
(2, 3, 'Felix', '2018-11-20'),    -- 2 (Brown's Maine Coon)
(3, 5, 'Charlie', '2022-03-15'),  -- 3 (Wilson's Cockatiel)
(4, 6, 'Fluffy', '2023-01-05'),   -- 4 (Clark's Guinea Pig)
(5, 2, 'Duke', '2019-07-30'),     -- 5 (Johnson's Shepherd)
(2, 4, 'Baldy', '2021-08-12');    -- 6 (Brown's Sphynx, 2nd pet)

-- Doctors (3 specialists)
INSERT INTO doctor (full_name, specialization, experience_years) VALUES 
('Dr. Peter House', 'Surgeon/Traumatologist', 15), -- 1
('Dr. Mary Watson', 'General Practice', 8),        -- 2
('Dr. Kevin Bird', 'Avian/Exotic Specialist', 5);  -- 3

-- ===================================================================
-- 3. VACCINATIONS (10 records)
-- ===================================================================

INSERT INTO vaccination (pet_id, vaccine_id, date_administered, revaccination_date) VALUES 
(1, 1, '2021-06-10', '2022-06-10'), -- Rex, Dog complex
(1, 2, '2021-06-10', '2022-06-10'), -- Rex, Rabies
(1, 1, '2022-06-15', '2023-06-15'), -- Rex, Revaccination
(1, 2, '2022-06-15', '2023-06-15'), -- Rex, Rabies revaccination
(2, 3, '2019-12-01', '2020-12-01'), -- Felix, Cat complex
(2, 4, '2019-12-01', '2020-12-01'), -- Felix, Rabies
(2, 3, '2020-12-05', '2021-12-05'), -- Felix, Revaccination
(5, 1, '2020-08-15', '2021-08-15'), -- Duke, Dog complex
(5, 2, '2020-08-15', '2021-08-15'), -- Duke, Rabies
(6, 3, '2022-09-10', '2023-09-10'); -- Baldy, Cat complex

-- ===================================================================
-- 4. VISITS AND MEDICAL HISTORY (12 visits)
-- ===================================================================

INSERT INTO visit (pet_id, doctor_id, visit_datetime, general_notes) VALUES 
(1, 2, '2023-10-01 10:00:00', 'Routine annual checkup.'),                               -- 1 (Rex)
(2, 2, '2023-10-05 14:30:00', 'Complaints of nausea after eating. Suspected gastritis.'), -- 2 (Felix)
(3, 3, '2023-10-10 11:15:00', 'Bird is plucking feathers on its chest.'),               -- 3 (Charlie)
(5, 1, '2023-10-15 19:45:00', 'Hit by a scooter, not stepping on the front paw.'),      -- 4 (Duke)
(6, 2, '2023-10-20 09:20:00', 'Dark discharge in the ears, shaking head.'),             -- 5 (Baldy)
(1, 2, '2023-11-01 16:00:00', 'Tick removed 3 days ago. Dark urine.'),                  -- 6 (Rex)
(4, 3, '2023-11-05 12:00:00', 'Sitting in the corner, refused hay since yesterday.'),   -- 7 (Fluffy)
(2, 2, '2023-11-10 14:00:00', 'Follow-up visit. Vomiting has stopped.'),                -- 8 (Felix)
(5, 1, '2023-11-15 10:30:00', 'Control X-ray, cast removal.'),                          -- 9 (Duke)
(6, 2, '2023-12-01 11:00:00', 'Ears are clean, treatment was successful.'),             -- 10 (Baldy)
(3, 3, '2023-12-15 13:20:00', 'Routine beak and nail trimming.'),                       -- 11 (Charlie)
(1, 2, '2024-01-10 15:00:00', 'Blood tests post-babesiosis are normal.');               -- 12 (Rex)

-- ===================================================================
-- 5. VISIT DETAILS (Junction Tables M:N)
-- ===================================================================

-- Visit Symptoms (visit_id, symptom_id)
INSERT INTO visit_symptom (visit_id, symptom_id) VALUES 
(2, 1), (2, 3), -- Visit 2 (Felix): Vomiting, Loss of appetite
(3, 4),         -- Visit 3 (Charlie): Itching
(4, 5), (4, 2), -- Visit 4 (Duke): Lameness, Lethargy
(5, 4),         -- Visit 5 (Baldy): Itching
(6, 2), (6, 3), -- Visit 6 (Rex): Lethargy, Loss of appetite
(7, 3), (7, 2); -- Visit 7 (Fluffy): Loss of appetite, Lethargy

-- Visit Diagnoses (visit_id, diagnosis_id, is_primary)
INSERT INTO visit_diagnosis (visit_id, diagnosis_id, is_primary) VALUES 
(1, 6, TRUE),  -- Rex: Healthy
(2, 1, TRUE),  -- Felix: Gastritis
(3, 4, TRUE),  -- Charlie: Dermatitis
(4, 5, TRUE),  -- Duke: Fracture
(5, 2, TRUE),  -- Baldy: Otitis
(6, 3, TRUE),  -- Rex: Babesiosis
(7, 1, TRUE),  -- Fluffy: Gastritis
(8, 1, TRUE),  -- Felix: Gastritis (follow-up)
(9, 5, TRUE),  -- Duke: Fracture (follow-up)
(10, 2, TRUE), -- Baldy: Otitis (follow-up)
(11, 6, TRUE), -- Charlie: Healthy
(12, 6, TRUE); -- Rex: Healthy

-- Visit Treatments (visit_id, treatment_id, dosage, duration)
INSERT INTO visit_treatment (visit_id, treatment_id, dosage, duration) VALUES 
(1, 5, '1 tablet per day', '30 days'),        -- Rex: Vitamins
(2, 1, '50 mg twice a day', '7 days'),        -- Felix: Antibiotic
(2, 2, '100 ml subcutaneously', 'Single use'),-- Felix: Saline
(3, 5, 'Add to water', '14 days'),            -- Charlie: Vitamins
(4, 6, 'Front paw fixation', '30 days'),      -- Duke: Cast
(4, 1, '250 mg twice a day', '10 days'),      -- Duke: Antibiotic
(5, 3, '3 drops per ear', '14 days'),         -- Baldy: Ear flushing
(5, 4, 'Thin layer', '7 days'),               -- Baldy: Ointment
(6, 2, '500 ml IV', 'Daily for 3 days'),      -- Rex: IV Fluids
(7, 5, '1 ml orally', '5 days');              -- Fluffy: Vitamins