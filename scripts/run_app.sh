
# Set Graph API token as environment variable:
token=`head -n 1 /home/skems/ceweb/config/keys/facebook_graph_api_user_access_token_upto_2022-09-18.txt`
export TOKEN=$token

cd ../src/

streamlit run app.py
