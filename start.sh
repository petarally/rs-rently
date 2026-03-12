#!/bin/bash

echo "=========================================="
echo "🚗 RS-Rently Rent-a-Car Sustav"
echo "=========================================="
echo ""
echo "Pokrećem mikroservise..."
echo ""

docker-compose up --build

echo ""
echo "=========================================="
echo "✅ Sustav pokrenut!"
echo "=========================================="
echo ""
echo "📱 Otvori u pregledniku:"
echo "   👉 http://localhost:3000"
echo ""
echo "🔐 Demo pristup:"
echo "   Username: admin"
echo "   Password: admin"
echo ""
echo "📊 Za logove:"
echo "   docker-compose logs -f [service-name]"
echo ""
echo "⛔ Za zaustavljanje:"
echo "   docker-compose down"
echo ""
