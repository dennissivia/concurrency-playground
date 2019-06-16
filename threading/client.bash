
function send_request(){
  i=${1}
  echo "request for client $i" | nc localhost 1238
}

for i in `seq 1 10`; do
  echo "client: $i is next"
  send_request $i &
done
echo "client done"
