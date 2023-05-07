-- CreateEnum
CREATE TYPE "IrrigationType" AS ENUM ('time', 'period');

-- CreateEnum
CREATE TYPE "DayOfWeek" AS ENUM ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'everyday');

-- CreateTable
CREATE TABLE "User" (
    "id" TEXT NOT NULL,
    "email" VARCHAR(255) NOT NULL,
    "first_name" VARCHAR(255) NOT NULL,
    "last_name" VARCHAR(255) NOT NULL,
    "password" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Verification" (
    "id" TEXT NOT NULL,
    "verified" BOOLEAN NOT NULL DEFAULT false,
    "verified_at" TIMESTAMP(3) NOT NULL,
    "user_id" TEXT NOT NULL,

    CONSTRAINT "Verification_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Plant" (
    "id" TEXT NOT NULL,
    "chip_id" VARCHAR(16) NOT NULL,
    "name" VARCHAR(255) NOT NULL DEFAULT 'New Plant',
    "water_amount" INTEGER NOT NULL DEFAULT 1000,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    "auto_irrigation" BOOLEAN NOT NULL DEFAULT true,
    "moisture_percentage_treshold" INTEGER NOT NULL DEFAULT 50,
    "irrigation_type" "IrrigationType" NOT NULL DEFAULT 'period',
    "periodstamp_times_a_week" INTEGER NOT NULL DEFAULT 0,
    "user_id" TEXT NOT NULL,

    CONSTRAINT "Plant_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "MoisturePercentageRecord" (
    "id" TEXT NOT NULL,
    "percentage" INTEGER NOT NULL,
    "at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "plant_id" TEXT NOT NULL,

    CONSTRAINT "MoisturePercentageRecord_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "IrrigationRecord" (
    "id" TEXT NOT NULL,
    "water_amount" INTEGER NOT NULL DEFAULT 1000,
    "at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "plant_id" TEXT NOT NULL,

    CONSTRAINT "IrrigationRecord_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Timestamp" (
    "id" TEXT NOT NULL,
    "day_of_week" "DayOfWeek" NOT NULL DEFAULT 'everyday',
    "hour" INTEGER NOT NULL,
    "minute" INTEGER NOT NULL,
    "plant_id" TEXT NOT NULL,

    CONSTRAINT "Timestamp_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Periodstamp" (
    "id" TEXT NOT NULL,
    "day_of_week" "DayOfWeek" NOT NULL DEFAULT 'everyday',
    "hour" INTEGER NOT NULL,
    "minute" INTEGER NOT NULL,
    "plant_id" TEXT NOT NULL,

    CONSTRAINT "Periodstamp_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");

-- CreateIndex
CREATE UNIQUE INDEX "Verification_user_id_key" ON "Verification"("user_id");

-- CreateIndex
CREATE UNIQUE INDEX "Plant_chip_id_key" ON "Plant"("chip_id");

-- AddForeignKey
ALTER TABLE "Verification" ADD CONSTRAINT "Verification_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Plant" ADD CONSTRAINT "Plant_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "MoisturePercentageRecord" ADD CONSTRAINT "MoisturePercentageRecord_plant_id_fkey" FOREIGN KEY ("plant_id") REFERENCES "Plant"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "IrrigationRecord" ADD CONSTRAINT "IrrigationRecord_plant_id_fkey" FOREIGN KEY ("plant_id") REFERENCES "Plant"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Timestamp" ADD CONSTRAINT "Timestamp_plant_id_fkey" FOREIGN KEY ("plant_id") REFERENCES "Plant"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Periodstamp" ADD CONSTRAINT "Periodstamp_plant_id_fkey" FOREIGN KEY ("plant_id") REFERENCES "Plant"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
