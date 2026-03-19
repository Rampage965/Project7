// --- 1. SETUP ---
var currentMove = 1.0; 
var currentBPM = 0; 

Bangle.setHRMPower(1);
Bangle.setLCDPower(1);
Bangle.setLCDTimeout(0); 

// --- 2. SENSORS ---
Bangle.on('accel', function(a) {
  // Constant background monitoring
  currentMove = Math.sqrt(a.x*a.x + a.y*a.y + a.z*a.z);
});

Bangle.on('HRM', function(sensor) {
  currentBPM = sensor.bpm;
});

// --- 3. INITIAL SCREEN ---
g.clear();
g.setFont("Vector", 20).setFontAlign(0,0);
g.setColor("#00FFFF").drawString("CONNECTED", g.getWidth()/2, g.getHeight()/2);
g.setFont("6x8", 1).drawString("Streaming @ 5Hz", g.getWidth()/2, g.getHeight()/2 + 30);
g.flip();

// --- 4. HIGH-SPEED TRANSMISSION ---
setInterval(function() {
  // Send JSON immediately
  Bluetooth.println(JSON.stringify({
    "bpm": currentBPM, 
    "accel": currentMove.toFixed(2)
  }));
  

  
}, 50);