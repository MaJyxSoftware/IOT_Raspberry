
echo "=== Installing requirements ==="
pip install -r requirements.txt

echo "=== Installing daemon ==="
cp dht.py /usr/local/bin/sensor-dhtd
chmod +x /usr/local/bin/sensor-dhtd

mkdir -p /etc/sensors
mkdir -p /var/run/sensors

echo "=== Installing service ==="
cp sensor-dht.service /etc/systemd/system/sensor-dht.service
systemctl daemon-reload

echo "=== Enabling service ==="
systemctl enable sensor-dht.service

echo "=== Starting service ==="
systemctl start sensor-dht.service
