banner()
{
  echo "+------------------------------------------+"
  printf "| %-40s |\n" "`date`"
  echo "|                                          |"
  printf "|`tput bold` %-40s `tput sgr0`|\n" "$@"
  echo "+------------------------------------------+"
}

banner "Starting the server"
sleep 3

cd /Users/juspay/nammayatri/Backend
set +x
make stop-all-containers
make run-pgadmin
echo "Go and sleep for 45 seconds."
sleep 45
make run-mobility-stack
