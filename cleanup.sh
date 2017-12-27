 find ./ -type f -name "*.py" -exec sh -c '
  autoflake "$0" -i --remove-all-unused-imports --remove-unused-variables -r 
' {} \;
