ngrok http 8000 > /dev/null &
sleep 2
NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | grep -o 'https://[^"]*')
export NGROK_DOMAIN=$NGROK_URL
uv run manage.py runserver