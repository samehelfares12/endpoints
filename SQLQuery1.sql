-- Step 1: Create the database
CREATE DATABASE HorseApp;
GO

-- Use the newly created database
USE HorseApp;
GO

-- Step 2: Create the Users table
CREATE TABLE Users (
    user_id INT IDENTITY(1,1) PRIMARY KEY,
    user_name NVARCHAR(100) NOT NULL,
    email NVARCHAR(255) UNIQUE NOT NULL,
    password NVARCHAR(255) NOT NULL,
    profile_picture NVARCHAR(255) NULL
);
GO

-- Step 3: Create the Horses table
CREATE TABLE Horses (
    horse_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    gender NVARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    breed NVARCHAR(100) NOT NULL,
    coat NVARCHAR(100) NOT NULL,
    country_of_birth NVARCHAR(100) NOT NULL,
    breeder NVARCHAR(255) NULL,
    price DECIMAL(10,2) NULL,
    national_id NVARCHAR(50) UNIQUE NOT NULL,
    owner_id INT NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES Users(user_id) ON DELETE CASCADE
);
GO

-- Step 4: Procedure to Insert a Horse for the Currently Logged-in User
CREATE PROCEDURE AddHorse
    @current_user_id INT,  -- Pass the currently logged-in user's ID
    @name NVARCHAR(100),
    @gender NVARCHAR(50),
    @date_of_birth DATE,
    @breed NVARCHAR(100),
    @coat NVARCHAR(100),
    @country_of_birth NVARCHAR(100),
    @breeder NVARCHAR(255),
    @price DECIMAL(10,2),
    @national_id NVARCHAR(50)
AS
BEGIN
    INSERT INTO Horses (name, gender, date_of_birth, breed, coat, country_of_birth, breeder, price, national_id, owner_id)
    VALUES (@name, @gender, @date_of_birth, @breed, @coat, @country_of_birth, @breeder, @price, @national_id, @current_user_id);
END;
GO
