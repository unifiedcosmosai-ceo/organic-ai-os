#!/bin/bash
set -e

echo "🧬 Installing Organic AI Organism..."

INSTALL_DIR="/opt/organic_ai_platform"
SERVICE_NAME="organic-organism.service"

# 1. Copy files
sudo mkdir -p $INSTALL_DIR
sudo cp -r . $INSTALL_DIR/
sudo chown -R $USER:$USER $INSTALL_DIR

# 2. Install Docker if missing
if ! command -v docker &> /dev/null; then
  echo "Installing Docker..."
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker $USER
fi

# 3. Systemd service
echo "Installing systemd service..."
sudo cp organic-organism.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME

# 4. Timer for nightly evolution at 02:00 (alternative to internal scheduler)
cat <<EOF | sudo tee /etc/systemd/system/organic-organism-nightly.service
[Unit]
Description=Organic Organism Nightly Evolution Trigger
After=organic-organism.service

[Service]
Type=oneshot
ExecStart=/usr/bin/docker exec organic_ai_organism python -c "from autonomous_organism import OrganismMemory, FastaWatcher, NightlyEvolution; m=OrganismMemory(); w=FastaWatcher(m); NightlyEvolution(m,w).run_nightly()"
EOF

cat <<EOF | sudo tee /etc/systemd/system/organic-organism-nightly.timer
[Unit]
Description=Run Organic Organism Evolution nightly at 02:00

[Timer]
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable organic-organism-nightly.timer
sudo systemctl start organic-organism-nightly.timer

# 5. Start
echo "Starting organism..."
sudo systemctl start $SERVICE_NAME

echo ""
echo "✅ Organism installed!"
echo "  Status: sudo systemctl status $SERVICE_NAME"
echo "  Logs: sudo journalctl -u $SERVICE_NAME -f"
echo "  Inbox: $INSTALL_DIR/fasta_inbox/"
echo "  Memory: $INSTALL_DIR/memory/"
echo "  Timer: sudo systemctl status organic-organism-nightly.timer"
echo ""
echo "  Docker logs: docker logs -f organic_ai_organism"
