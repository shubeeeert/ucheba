-- ===================================================================
-- Reference Data
-- ===================================================================

CREATE TABLE species (
    species_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    -- Enforce allowed species list
    CONSTRAINT chk_species_name CHECK (
        name IN ('Dog', 'Cat', 'Bird', 'Rodent', 'Reptile', 'Exotic Animal')
    )
);

CREATE TABLE breed (
    breed_id SERIAL PRIMARY KEY,
    species_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    FOREIGN KEY (species_id) REFERENCES species(species_id) ON DELETE CASCADE,
    -- Ensure breed name is unique per species
    CONSTRAINT uq_breed_species UNIQUE (species_id, name)
);

CREATE TABLE symptom (
    symptom_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE diagnosis (
    diagnosis_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    icd_code VARCHAR(20) UNIQUE -- ICD code (optional but unique)
);

CREATE TABLE treatment (
    treatment_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE vaccine (
    vaccine_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    manufacturer VARCHAR(100)
);

-- ===================================================================
-- Core Entities
-- ===================================================================

CREATE TABLE owner (
    owner_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    -- Validate phone: starts with optional +, followed by 10-15 digits
    phone VARCHAR(20) NOT NULL UNIQUE 
        CONSTRAINT chk_owner_phone CHECK (phone ~ '^\+?[0-9]{10,15}$'),
    -- Validate email format
    email VARCHAR(255) UNIQUE 
        CONSTRAINT chk_owner_email CHECK (email ~* '^[A-Za-z0-9._+%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$')
);

CREATE TABLE pet (
    pet_id SERIAL PRIMARY KEY,
    owner_id INT, -- Nullable to allow ON DELETE SET NULL
    breed_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    birth_date DATE,
    FOREIGN KEY (owner_id) REFERENCES owner(owner_id) ON DELETE SET NULL,
    FOREIGN KEY (breed_id) REFERENCES breed(breed_id) ON DELETE RESTRICT,
    -- Prevent future birth dates
    CONSTRAINT chk_pet_birth_date CHECK (birth_date <= CURRENT_DATE)
);

CREATE TABLE doctor (
    doctor_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    experience_years INT DEFAULT 0 NOT NULL,
    -- Experience bounds check (0 to 70 years)
    CONSTRAINT chk_doctor_experience CHECK (experience_years >= 0 AND experience_years <= 70)
);

-- ===================================================================
-- Transactional Entities
-- ===================================================================

CREATE TABLE visit (
    visit_id SERIAL PRIMARY KEY,
    pet_id INT NOT NULL,
    doctor_id INT NOT NULL,
    visit_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    general_notes TEXT,
    FOREIGN KEY (pet_id) REFERENCES pet(pet_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id) ON DELETE RESTRICT
);

CREATE TABLE vaccination (
    vaccination_id SERIAL PRIMARY KEY,
    pet_id INT NOT NULL,
    vaccine_id INT NOT NULL,
    date_administered DATE DEFAULT CURRENT_DATE NOT NULL,
    revaccination_date DATE,
    FOREIGN KEY (pet_id) REFERENCES pet(pet_id) ON DELETE CASCADE,
    FOREIGN KEY (vaccine_id) REFERENCES vaccine(vaccine_id) ON DELETE RESTRICT,
    -- Revaccination must occur after administration date
    CONSTRAINT chk_revaccination_date CHECK (revaccination_date > date_administered)
);

-- ===================================================================
-- Junction Tables (M:N)
-- ===================================================================

CREATE TABLE visit_symptom (
    visit_id INT NOT NULL,
    symptom_id INT NOT NULL,
    PRIMARY KEY (visit_id, symptom_id),
    FOREIGN KEY (visit_id) REFERENCES visit(visit_id) ON DELETE CASCADE,
    FOREIGN KEY (symptom_id) REFERENCES symptom(symptom_id) ON DELETE CASCADE
);

CREATE TABLE visit_diagnosis (
    visit_id INT NOT NULL,
    diagnosis_id INT NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE NOT NULL,
    PRIMARY KEY (visit_id, diagnosis_id),
    FOREIGN KEY (visit_id) REFERENCES visit(visit_id) ON DELETE CASCADE,
    FOREIGN KEY (diagnosis_id) REFERENCES diagnosis(diagnosis_id) ON DELETE CASCADE
);

CREATE TABLE visit_treatment (
    visit_id INT NOT NULL,
    treatment_id INT NOT NULL,
    dosage VARCHAR(100) NOT NULL,
    duration VARCHAR(100) NOT NULL,
    PRIMARY KEY (visit_id, treatment_id),
    FOREIGN KEY (visit_id) REFERENCES visit(visit_id) ON DELETE CASCADE,
    FOREIGN KEY (treatment_id) REFERENCES treatment(treatment_id) ON DELETE CASCADE
);