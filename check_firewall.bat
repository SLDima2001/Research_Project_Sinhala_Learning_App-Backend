@echo off
echo Checking if port 5001 is accessible...
echo.

echo Testing localhost connection...
curl -s http://127.0.0.1:5001/health
echo.

echo Testing IP address connection...
curl -s http://192.168.1.4:5001/health
echo.

echo.
echo If you see JSON responses above, the server is working!
echo If not, you may need to add a firewall rule.
echo.
echo Press any key to add firewall rule (requires admin)...
pause

echo Adding firewall rule for port 5001...
netsh advfirewall firewall add rule name="Python Flask App - Port 5001" dir=in action=allow protocol=TCP localport=5001

echo.
echo Firewall rule added! Try connecting from your phone again.
pause
