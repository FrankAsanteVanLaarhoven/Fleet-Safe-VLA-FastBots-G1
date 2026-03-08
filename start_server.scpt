try
	display dialog "Starting GCP Isaac L4 Dev Server..." buttons {"OK"} default button 1 giving up after 2
	do shell script "/bin/zsh -c 'source ~/.zshrc 2>/dev/null; /opt/homebrew/bin/gcloud compute instances start isaac-l4-dev --zone=us-central1-a --project=project-1fa64e91-d51b-4ea2-a9d'"
	display dialog "Server is now RUNNING!" buttons {"OK"} default button 1
on error errMsg
	display dialog "Failed to start server: " & errMsg buttons {"OK"} default button 1
end try
