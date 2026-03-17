// --- 1. SETUP THE MEMORY ---
// We need a list to remember the last 140 heart beats so we can draw them
var pastHeartRates = new Float32Array(140); 

// Turn everything on
Bangle.setHRMPower(1); 
Bangle.setLCDPower(1); 

// --- 2. THE MAIN ACTION ---
// Every time the sensor feels a pulse, do this:
Bangle.on('HRM', function(sensor) {
  
  // A. SHIFT THE DATA: Move every old heart rate one step to the left
  for (var i = 0; i < pastHeartRates.length - 1; i++) {
    pastHeartRates[i] = pastHeartRates[i + 1];
  }
  
  // B. RECORD NEW DATA: Add the latest BPM to the very end of our list
  pastHeartRates[pastHeartRates.length - 1] = sensor.bpm;

  // C. CLEAN SCREEN: Wipe it black so we can draw the new frame
  g.clear();
  
  // D. DRAW THE FRAME: Draw a white "L" shape for our X and Y axes
  g.setColor("#FFFFFF"); 
  g.drawLine(30, 40, 30, 160);  // The upright line (BPM)
  g.drawLine(30, 160, 170, 160); // The bottom line (Time)
  
  // E. LABELS: Put numbers on the side so we know the scale
  g.setFont("6x8", 1).setFontAlign(-1, 0);
  g.drawString("140 -", 5, 60);
  g.drawString("100 -", 5, 100);
  g.drawString(" 60 -", 5, 140);

  // F. DRAW THE GREEN LINE: Loop through our list and connect the dots
  g.setColor("#00FF00"); 
  for (var x = 0; x < pastHeartRates.length - 1; x++) {
    var firstDot = pastHeartRates[x];
    var secondDot = pastHeartRates[x + 1];

    // Only draw if we have a real reading for both dots
    if (firstDot > 0 && secondDot > 0) {
      // Map the heart rate to the screen height (Higher BPM = Higher Line)
      var height1 = 160 - (firstDot - 40); 
      var height2 = 160 - (secondDot - 40);
      
      // Draw the line connecting the two dots
      g.drawLine(x + 30, height1, x + 31, height2);
    }
  }

  // G. TEXT AT TOP: Show the big number and the trust percentage
  g.setColor("#FFFFFF");
  g.setFont("6x8", 2).setFontAlign(0, -1);
  g.drawString("BPM: " + sensor.bpm, 88, 5);
  
  // H. BLUETOOTH: Send the data to your VS Code script
  Bluetooth.println(JSON.stringify({
    "bpm": sensor.bpm, 
    "conf": sensor.confidence
  }));
});