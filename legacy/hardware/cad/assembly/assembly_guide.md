# OpenReef System Assembly Guide

Complete step-by-step assembly instructions for the OpenReef automated assay system.

## Before You Begin

### Required Tools

- [ ] Phillips screwdriver (PH1)
- [ ] Hex driver set (2mm, 2.5mm, 3mm)
- [ ] Wire strippers
- [ ] Wire cutters
- [ ] Soldering iron + solder (for electronics)
- [ ] Hot glue gun (optional, for strain relief)
- [ ] Multimeter (for testing connections)
- [ ] Cable ties (various sizes)
- [ ] Isopropyl alcohol (for cleaning)

### Printed Components Checklist

- [ ] Main enclosure body
- [ ] Enclosure top panel
- [ ] PyBadge cover/mount
- [ ] Cuvette holder (dual LED)
- [ ] 4× Bottle caps (3-port)
- [ ] 2× Pump mounting brackets
- [ ] 1× Valve mounting plate
- [ ] Standoffs/spacers (if not integrated)

### Electronic Components

- [ ] AdaFruit PyBadge
- [ ] AS7341 Colorimeter sensor
- [ ] DC Motor + Stepper FeatherWing (PID 3243)
- [ ] 8-Channel Solenoid Driver (PID 6318)
- [ ] 3× 6V Air Valves (PID 4663)
- [ ] Green LED (528nm)
- [ ] Red LED (625nm)
- [ ] Power supply (12V, 2-3A)
- [ ] STEMMA QT cables (I2C connections)

### Fluidic Components

- [ ] 2× Peristaltic pumps (DC motor)
- [ ] Silicone tubing - 3mm ID (PID 4661)
- [ ] Silicone tubing - 6mm ID (for water)
- [ ] Tube connectors (barbed, various sizes)
- [ ] 3× Magnetic stirrers (small DC motors)
- [ ] 3× Stir bars (10mm PTFE)
- [ ] Cuvettes (1cm path, glass or plastic)

### Hardware (Fasteners)

- [ ] 20× M3 × 10mm screws (panel assembly)
- [ ] 8× M3 × 20mm screws (pump mounts)
- [ ] 28× M3 nuts
- [ ] 12× M2.5 × 8mm screws (PyBadge, electronics)
- [ ] 8× M2.5 standoffs (15mm)
- [ ] 4× M4 × 16mm screws (pump mounting)
- [ ] 4× Rubber feet
- [ ] 20× Cable ties
- [ ] 4× O-rings (for bottle caps)

### Reagents & Consumables

- [ ] API Phosphate test kit
- [ ] API Nitrate test kit
- [ ] Phosphate standard (1000 ppm)
- [ ] Nitrate standard (4430 ppm)
- [ ] Distilled/RO water supply

## Assembly Steps

### Phase 1: Enclosure Preparation (30 min)

#### 1.1 Clean Printed Parts

1. Remove all support material from 3D printed parts
2. Clean with isopropyl alcohol
3. Sand any rough edges with 220-grit sandpaper
4. Check that all screw holes are clear (drill out if needed)

#### 1.2 Install Threaded Inserts (Optional but Recommended)

For better thread strength in plastic:

1. Heat M3 threaded inserts with soldering iron
2. Press into mounting holes
3. Let cool completely
4. Test with screw (should thread smoothly)

**Locations:**
- Pump mounting bosses (8 inserts)
- Valve plate standoffs (4 inserts)
- Electronics bay standoffs (8 inserts)
- Panel assembly points (20 inserts)

#### 1.3 Install Rubber Feet

1. Flip enclosure upside down
2. Mark foot positions (one at each corner, ~20mm from edge)
3. Clean bottom surface with isopropyl alcohol
4. Peel adhesive backing from rubber feet
5. Press firmly into position

### Phase 2: Optical System (45 min)

#### 2.1 Install LEDs in Cuvette Holder

**Green LED (528nm for Nitrate):**

1. Insert green LED into one LED mount hole
2. Orient flat edge correctly (cathode marking)
3. Bend leads 90° to secure
4. Solder ~20cm wires to LED leads
   - Red wire → Anode (longer lead)
   - Black wire → Cathode (shorter lead, flat side)
5. Apply heat shrink tubing
6. Secure LED with small amount of hot glue

**Red LED (625nm for Phosphate):**

1. Repeat above steps for red LED in opposite mount
2. Install in 180° position from green LED

**Current Limiting Resistors:**
- Calculate: R = (Vsupply - VLED) / I
- For 5V supply, 20mA LED: R ≈ 150Ω
- Solder resistor in series with each LED

#### 2.2 Install AS7341 Sensor

1. Position AS7341 breakout board opposite LEDs
2. Align sensor window with cuvette center
3. Mark mounting holes
4. Install M2 standoffs (if not integrated)
5. Secure sensor with 2× M2 screws
6. Connect STEMMA QT cable to sensor

**Verify Alignment:**
- LED → Cuvette Center → Sensor should be straight line
- Distance: ~50mm from LED to sensor
- Test fit cuvette - should drop in easily

#### 2.3 Install Cuvette Holder in Enclosure

1. Position cuvette holder on front panel
2. Align with mounting holes
3. Secure with 4× M3 × 10mm screws
4. Route LED and sensor cables through cable channel
5. Verify cuvette inserts and removes smoothly

#### 2.4 Install Magnetic Stirrer

Below cuvette holder:

1. Mount small DC motor (stirrer) to underside
2. Attach magnet to motor shaft
   - Use disk magnet (10-15mm diameter)
   - Secure with hot glue or set screw
3. Route motor wires through cable channel
4. Test: Insert stir bar in cuvette, power motor
   - Stir bar should spin smoothly
   - Adjust distance if not coupling properly

### Phase 3: Fluidics (90 min)

#### 3.1 Install Peristaltic Pumps

**FeW Pump (Water):**

1. Attach pump to mounting bracket using M4 screws
2. Position bracket on right side panel
3. Secure bracket to enclosure with 4× M3 × 20mm screws
4. Route motor wires to electronics bay

**FeR Pump (Reagent):**

1. Repeat above for second pump
2. Position below FeW pump
3. Label pumps clearly (FeW and FeR)

**Tubing Installation:**

1. Open pump head (usually has release lever)
2. Insert tubing:
   - FeW: 6mm ID silicone tubing
   - FeR: 3mm ID silicone tubing
3. Close pump head (tubing should be compressed)
4. Verify tubing can be pulled through by rotating pump manually

#### 3.2 Install Valve Mounting Plate

1. Position valve plate on bottom of enclosure
2. Align mounting holes with standoffs
3. Secure with 4× M3 × 20mm screws
4. Plate should be elevated ~10mm above bottom (for tubing clearance)

#### 3.3 Install Solenoid Valves

Mount 3 valves to plate:

**ReV (Reagent Valve):**

1. Position in first mounting location
2. Secure with 2× M3 × 10mm screws
3. Connect JST connector to valve
4. Label clearly: "ReV - Reagent #1/#2"

**WtV (Water Test Valve):**

1. Mount in center position
2. Label: "WtV - RO/Test Water"

**WaV (Waste Valve):**

1. Mount in third position
2. Label: "WaV - Waste/Test"

**Wire Routing:**
- Route valve wires through cable channel
- Keep wires organized with cable ties
- Leave slack for maintenance access

#### 3.4 Connect Tubing Network

This is the most complex part. Refer to fluidic diagram in specifications.md.

**From FeW Pump:**
- Input: Connect to WtV valve (common port)
- Output: Connect to cuvette (via WaV valve)

**WtV Valve Connections:**
- Port A: RO water bottle
- Port B: Test water bottle
- Common: To FeW pump input

**WaV Valve Connections:**
- Port A: Waste container
- Port B: Cuvette
- Common: From FeW pump output

**From FeR Pump:**
- Input: Connect to ReV valve (common port)
- Output: Connect to cuvette (tee into FeW output line)

**ReV Valve Connections:**
- Port A: Reagent #1 bottle
- Port B: Reagent #2 bottle
- Common: To FeR pump input

**Tips:**
- Use barbed connectors for all joints
- Ensure tight fit (tubing should not pull off easily)
- Avoid kinks in tubing
- Mark tubing with colored tape for identification
- Prime system with water to check for leaks

#### 3.5 Install Bottle Caps

For each bottle (RO, test water, reagent 1, reagent 2):

1. Drill holes in bottle cap if not pre-existing
2. Or use printed 3-port caps:
   - Port 1: Main tube (in/out)
   - Port 2: Air vent or secondary line
   - Port 3: Spare
3. Install o-ring in groove (if designed)
4. Insert tubes through ports
5. Ensure air-tight seal
6. Test cap on bottle - should thread smoothly

#### 3.6 Install Reagent Bottle Stirrers

For Reagent #2 bottle (critical for nitrate assay):

1. Mount small DC motor to bottle cap or platform
2. Attach magnet to shaft
3. Position stir bar in reagent bottle
4. Test stirring action
5. Route motor wires to electronics bay

Optional: Add stirrer to Reagent #1 as well.

### Phase 4: Electronics (60 min)

#### 4.1 Install Power Distribution

In electronics bay:

1. Mount terminal block or distribution board
2. Connect 12V power supply input
3. Create distribution:
   - 12V rail → Solenoid driver, pump motor driver
   - 5V rail (if using regulator) → Stirrers
4. Add fuses (recommended):
   - Main 12V: 3A fuse
   - 5V: 1A fuse

#### 4.2 Install Solenoid Driver (PID 6318)

1. Mount to standoffs in electronics bay with M2.5 screws
2. Connect I2C:
   - STEMMA QT cable to PyBadge
   - Daisy chain if using multiple I2C devices
3. Connect power:
   - VIN: 12V from distribution
   - GND: Common ground
4. Connect valve outputs:
   - Channel 0: ReV (Reagent Valve)
   - Channel 1: WtV (Water Test Valve)
   - Channel 2: WaV (Waste Valve)
   - Channels 3-7: Spare (for future expansion)

#### 4.3 Install DC Motor FeatherWing (PID 3243)

1. Mount to standoffs with M2.5 screws
2. Connect I2C (STEMMA QT)
3. Connect power (12V motor supply)
4. Connect pumps:
   - Motor 1: FeW pump
   - Motor 2: FeR pump
5. Connect stirrers (if controlled via this board):
   - Motor 3: Cuvette stirrer
   - Motor 4: Reagent stirrer

**Alternative:** Use PWM outputs from PyBadge for stirrers

#### 4.4 Install PyBadge

1. Position PyBadge in front panel mount
2. Secure with 4× M2.5 × 8mm screws
3. Connect I2C bus:
   - STEMMA QT to solenoid driver
   - STEMMA QT to motor driver
4. Connect GPIO:
   - LEDs (if not on motor driver)
   - Sensor (AS7341) I2C
5. Connect power:
   - USB-C from external power
   - Or battery pack if portable

#### 4.5 Wire Management

1. Bundle wires with cable ties
2. Route through cable channels
3. Label all connections
4. Use different colored wires for:
   - Red: Power (+)
   - Black: Ground (-)
   - Other colors: Signals
5. Leave slack for maintenance
6. Secure bundles at tie points

### Phase 5: Final Assembly & Testing (45 min)

#### 5.1 Install Bottles

1. Place bottles in holders:
   - RO water (large bottle, front left)
   - Test water (large bottle, front right)
   - Reagent #1 (smaller, rear left)
   - Reagent #2 (smaller, rear right)
2. Install caps with tubing
3. Verify bottles sit securely

#### 5.2 Connect Waste

1. Position waste container externally (rear of unit)
2. Route waste tube through grommet hole
3. Secure with clip or holder

#### 5.3 Close Enclosure

1. Verify all components installed
2. Check for any loose screws or connections
3. Install top panel
4. Secure with 6× M3 screws (hand-tight with knurled knobs)

#### 5.4 Power On Test

**DO NOT add reagents yet - use water only for testing**

1. Fill RO water bottle
2. Fill test water bottle with plain water
3. Connect power supply (12V)
4. Connect PyBadge USB (5V)
5. Power on

**Check:**
- [ ] PyBadge displays boot screen
- [ ] No smoke or burning smell
- [ ] All LEDs power on (if auto-initialized)
- [ ] Motors respond to test commands

#### 5.5 Pump Test

From PyBadge menu: `System → Diagnostics → Test Pumps`

1. FeW pump forward: Should pump water from RO bottle
2. FeW pump reverse: Should return water
3. FeR pump forward: Test with water (not reagent yet)
4. FeR pump reverse: Test return

**Troubleshooting:**
- No flow: Check tubing connections
- Weak flow: Check for air bubbles, re-seat tubing in pump
- Wrong direction: Reverse motor wiring

#### 5.6 Valve Test

From PyBadge menu: `System → Diagnostics → Test Valves`

1. Cycle each valve
2. Listen for click (solenoid actuation)
3. Verify flow path changes

**Test sequence:**
1. WtV: Switch between RO and test water
   - Pump should draw from different bottles
2. WaV: Switch between waste and test
   - Observe where water flows
3. ReV: Will test later with reagents

#### 5.7 Stirrer Test

1. Place stir bar in cuvette
2. Fill cuvette with water
3. Activate stirrer from menu
4. Should see smooth rotation

**Troubleshooting:**
- No spin: Magnet too far, move motor closer
- Erratic: Magnetic coupling weak, stronger magnet needed
- Too fast: Reduce PWM duty cycle in firmware

#### 5.8 Colorimeter Test

From PyBadge menu: `System → Diagnostics → Light Test`

1. Green LED test:
   - LED should illuminate
   - Sensor should detect green light
2. Red LED test:
   - LED should illuminate
   - Sensor should detect red light
3. Baseline test:
   - Insert water-filled cuvette
   - Zero colorimeter
   - Should give stable reading

**Expected values:**
- Blank water: Absorbance near 0.00 (±0.05)
- Colored solution: Positive absorbance

### Phase 6: Calibration (2-3 hours)

See `../../docs/calibration/calibration-guide.md` for detailed procedures.

#### 6.1 Pump Calibration

1. Measure FeW pump flow rate
2. Measure FeR pump flow rate
3. Convert API "drops" to mL
4. Save calibration to PyBadge

#### 6.2 Colorimeter Calibration

**Phosphate:**
1. Prepare 7-8 standards (0-30 ppm)
2. Run automated calibration wizard
3. Generate calibration curve
4. Save to `phosphate_cal.json`

**Nitrate:**
1. Prepare 7-8 standards (0-90 ppm)
2. Run automated calibration wizard
3. Generate calibration curve
4. Save to `nitrate_cal.json`

### Phase 7: First Real Test (30 min)

#### 7.1 Load Reagents

**Safety: Wear gloves and eye protection**

1. Fill Reagent #1 bottle with API test kit Bottle #1
2. Fill Reagent #2 bottle with API test kit Bottle #2
3. **IMPORTANT for nitrate**: Shake Bottle #2 vigorously
4. Secure caps

#### 7.2 Run Phosphate Test

1. Prepare test water sample
2. Menu → Run Test → Phosphate
3. Follow on-screen prompts
4. Automated sequence should run (~12 min)
5. Record result

**Expected for known sample:**
- Compare to manual test
- Should agree within ±10%

#### 7.3 Run Nitrate Test

1. Prepare test water sample
2. Menu → Run Test → Nitrate
3. Automated sequence (~10 min)
4. Record result

#### 7.4 Verify Results

Compare automated results to:
- Manual API test kit results
- Known standards
- Expected values for your sample

**Acceptance criteria:**
- Within ±10% of expected
- Reproducible (run duplicates)

## Maintenance Schedule

### Daily (if running multiple tests)
- [ ] Empty waste container
- [ ] Refill RO water
- [ ] Check reagent levels

### Weekly
- [ ] Clean cuvette
- [ ] Wipe optical surfaces
- [ ] Check tubing for wear
- [ ] Verify stirrer operation

### Monthly
- [ ] Replace tubing
- [ ] Clean valves
- [ ] Run calibration verification
- [ ] Update firmware (if available)
- [ ] Backup calibration data

### As Needed
- [ ] Replace reagents (check expiration)
- [ ] Replace cuvette (if scratched)
- [ ] Recalibrate system
- [ ] Deep clean fluidics

## Troubleshooting Common Issues

| Problem | Possible Cause | Solution |
|---------|---------------|----------|
| Pump not running | Power issue | Check connections, fuses |
| | Motor driver error | Reset driver, check I2C |
| Valve not clicking | Power issue | Check solenoid driver power |
| | Bad valve | Test valve with multimeter |
| No colorimeter reading | Sensor disconnected | Check I2C connection |
| | LED not working | Check LED power, polarity |
| Leaks | Loose connection | Tighten barbed fittings |
| | Cracked tubing | Replace tubing |
| Inconsistent results | Air in lines | Prime system thoroughly |
| | Dirty cuvette | Clean with dilute acid |
| | Reagent expired | Replace reagents |

## Safety Reminders

⚠️ **IMPORTANT SAFETY INFORMATION**

### Electrical
- Use certified 12V power supply
- Do not modify when powered
- Keep liquids away from electronics
- Use proper fuse protection

### Chemical
- **Phosphate Bottle #1**: Contains sulfuric acid (corrosive)
- **Nitrate Bottle #2**: Contains cadmium (toxic heavy metal)
- Always wear gloves and eye protection
- Work in ventilated area
- Dispose of nitrate waste properly (hazardous waste)
- Follow API test kit MSDS

### General
- Keep out of reach of children
- Do not drink or pipette by mouth
- Wash hands after handling reagents
- Have spill kit available
- Know location of safety shower/eyewash

## Getting Help

If you encounter issues:

1. **Check documentation**: Review relevant sections
2. **System diagnostics**: Use PyBadge diagnostic menu
3. **Community**: Post on OpenReef forums/GitHub
4. **IoRodeo resources**: Original colorimeter documentation

## Congratulations!

Your OpenReef automated assay system is now assembled and ready for use!

Next steps:
- Run QC samples regularly
- Log all test results
- Track system performance
- Consider future enhancements (WiFi, additional assays, etc.)

Happy testing! 🧪🔬🐠
