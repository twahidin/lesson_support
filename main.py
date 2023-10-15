#No need SQLite
import streamlit as st
from streamlit_antd_components import menu, MenuItem
import streamlit_antd_components as sac
from main_bot import basebot_memory, basebot_qa_memory, clear_session_states, search_bot, basebot, basebot_qa
from kb_module import display_files,docs_uploader, delete_files
from vs_module import display_vectorstores, create_vectorstore, delete_vectorstores
from authenticate import login_function,check_password
from class_dash import download_data_table_csv
from lesson_plan import lesson_collaborator, lesson_commentator, lesson_bot, lesson_map_generator
#New schema move function fom settings
from database_schema import create_dbs
from database_module import manage_tables, delete_tables
from org_module import (
	has_at_least_two_rows,
	initialise_admin_account,
	load_user_profile,
	display_accounts,
	create_org_structure,
	check_multiple_schools,
	process_user_profile,
	remove_or_reassign_teacher_ui,
	reassign_student_ui,
	change_teacher_profile_ui
)
from pwd_module import reset_passwords, password_settings
from users_module import (
	link_users_to_app_function_ui,
	set_function_access_for_user,
	create_prompt_template,
	update_prompt_template,
	vectorstore_selection_interface,
	pre_load_variables,
	load_and_fetch_vectorstore_for_user,
	link_profiles_to_vectorstore_interface
)

from bot_settings import bot_settings_interface, load_bot_settings
from PIL import Image
import configparser
import ast


class ConfigHandler:
	def __init__(self):
		self.config = configparser.ConfigParser()
		self.config.read('config.ini')

	def get_value(self, section, key):
		value = self.config.get(section, key)
		try:
			# Convert string value to a Python data structure
			return ast.literal_eval(value)
		except (SyntaxError, ValueError):
			# If not a data structure, return the plain string
			return value

# Initialization
config_handler = ConfigHandler()

# Setting Streamlit configurations
st.set_page_config(layout="wide")

# Fetching secrets from Streamlit
DEFAULT_TITLE = st.secrets["default_title"]
SUPER_PWD = st.secrets["super_admin_password"]
SUPER = st.secrets["super_admin"]

# Fetching values from config.ini
DEFAULT_TEXT = config_handler.get_value('constants', 'DEFAULT_TEXT')
TCH = config_handler.get_value('constants', 'TCH')
STU = config_handler.get_value('constants', 'STU')
SA = config_handler.get_value('constants', 'SA')
AD = config_handler.get_value('constants', 'AD')
COTF = config_handler.get_value('constants', 'COTF')
META = config_handler.get_value('constants', 'META')
PANDAI = config_handler.get_value('constants', 'PANDAI')
MENU_FUNCS = config_handler.get_value('menu_lists', 'MENU_FUNCS')
META_BOT = config_handler.get_value('constants', 'META_BOT')
QA_BOT = config_handler.get_value('constants', 'QA_BOT')
LESSON_BOT = config_handler.get_value('constants', 'LESSON_BOT')
LESSON_COLLAB = config_handler.get_value('constants', 'LESSON_COLLAB')
LESSON_COMMENT = config_handler.get_value('constants', 'LESSON_COMMENT')
LESSON_MAP = config_handler.get_value('constants', 'LESSON_MAP')
REFLECTIVE = config_handler.get_value('constants', 'REFLECTIVE')
CONVERSATION = config_handler.get_value('constants', 'CONVERSATION')
MINDMAP = config_handler.get_value('constants', 'MINDMAP')
METACOG = config_handler.get_value('constants', 'METACOG')

def is_function_disabled(function_name):
	return st.session_state.func_options.get(function_name, True)


def initialize_session_state( menu_funcs, default_value):
	st.session_state.func_options = {key: default_value for key in menu_funcs.keys()}
	

def main():
	try:
		if "title_page"	not in st.session_state:
			st.session_state.title_page = DEFAULT_TITLE 

		st.title(st.session_state.title_page)
		sac.divider(label='ETD & ITD MOE Project', icon='house', align='center', direction='horizontal', dashed=False, bold=False)
		
		if "api_key" not in st.session_state:
			st.session_state.api_key = ""

		if "option" not in st.session_state:
			st.session_state.option = False
		
		if "login" not in st.session_state:
			st.session_state.login = False
		
		if "user" not in st.session_state:
			st.session_state.user = None
		
		if "openai_model" not in st.session_state:
			st.session_state.openai_model = st.secrets["default_model"]

		if "msg" not in st.session_state:
			st.session_state.msg = []

		if "rating" not in st.session_state:
			st.session_state.rating = False

		if "lesson_plan" not in st.session_state:
			st.session_state.lesson_plan = ""

		if "temp" not in st.session_state:
			st.session_state.temp = st.secrets["default_temp"]
		
		if "frequency_penalty" not in st.session_state:
			st.session_state.frequency_penalty = st.secrets["default_frequency_penalty"]

		if "presence_penalty" not in st.session_state:
			st.session_state.presence_penalty = st.secrets["default_presence_penalty"]

		if "k_memory" not in st.session_state:
			st.session_state.k_memory = st.secrets["default_k_memory"]
		
		if "memoryless" not in st.session_state:
			st.session_state.memoryless = False

		if "vs" not in st.session_state:
			st.session_state.vs = False
		
		if "visuals" not in st.session_state:
			st.session_state.visuals = False
		
		if "svg_height" not in st.session_state:
			st.session_state["svg_height"] = 1000
			
		if "current_model" not in st.session_state:
			st.session_state.current_model = "No KB loaded"

		if "func_options" not in st.session_state:
			st.session_state.func_options = {}
			initialize_session_state(MENU_FUNCS, True)

		create_dbs()
		initialise_admin_account()
		#PLEASE REMOVE THIS 
		#st.write("User Profile: ", st.session_state.user)
		
		#PLEASE REMOVE ABOVE
		with st.sidebar: #options for sidebar
			if st.session_state.login == False:
				image = Image.open('cotf_logo.png')
				st.image(image)
				st.session_state.option = menu([MenuItem('Users login', icon='people'), MenuItem('Application Info', icon='info-circle')])
			else:
				image = Image.open('pandai.jpeg')
				st.image(image)
				#can do a test if user is school is something show a different logo and set a different API key
				if st.session_state.user['profile_id'] == SA: #super admin login feature
					# Initialize the session state for function options	
					initialize_session_state(MENU_FUNCS, False)
				else:
					set_function_access_for_user(st.session_state.user['id'])
					# Using the is_function_disabled function for setting the `disabled` attribute
				st.session_state.option = sac.menu([
					sac.MenuItem('Home', icon='house', children=[
						sac.MenuItem('Class Dashboard', icon='person-circle', disabled=is_function_disabled('Personal Dashboard')),
						#sac.MenuItem('Class Dashboard', icon='clipboard-data', disabled=is_function_disabled('Class Dashboard')),
					]),
					sac.MenuItem('Lesson Assistant', icon='person-fill-gear', children=[
						sac.MenuItem('Lesson Collaborator', icon='pencil-square', disabled=is_function_disabled('Lesson Collaborator')),
						sac.MenuItem('Lesson Commentator', icon='chat-left-dots', disabled=is_function_disabled('Lesson Commentator')),
						sac.MenuItem('Lesson Designer Map', icon='diagram-2', disabled=is_function_disabled('Lesson Designer Map')),
						sac.MenuItem('Lesson Design Facilitator (Chatbot)', icon='chat-text', disabled=is_function_disabled('Lesson Design Facilitator')),
					]),
					sac.MenuItem('Dialogic Agent', icon='robot', children=[
						sac.MenuItem('Prototype Chatbot', icon='chat-square-dots', disabled=is_function_disabled('Prototype Chatbot')),
						sac.MenuItem('Bot & Prompt Management', icon='wrench', disabled=is_function_disabled('Chatbot Management')),
					]),
					sac.MenuItem('Knowledge Base Tools', icon='book', children=[
						sac.MenuItem('Files Management', icon='file-arrow-up', disabled=is_function_disabled('Files management')),
						sac.MenuItem('Knowledge Base Editor', icon='database-fill-up',disabled=is_function_disabled('KB management')),
					]),
					sac.MenuItem('Organisation Tools', icon='buildings', children=[
						sac.MenuItem('Org Management', icon='building-gear', disabled=is_function_disabled('Organisation Management')),
						sac.MenuItem('Users Management', icon='house-gear', disabled=is_function_disabled('School Users Management')),
					]),
					sac.MenuItem(type='divider'),
					sac.MenuItem('Profile Settings', icon='gear'),
					sac.MenuItem('Application Info', icon='info-circle'),
					sac.MenuItem('Logout', icon='box-arrow-right'),
				], index=1, format_func='title', open_all=False)

		if st.session_state.option == 'Users login':
				col1, col2 = st.columns([3,4])
				placeholder2 = st.empty()
				with placeholder2:
					with col1:
						if login_function() == True:
							placeholder2.empty()
							st.session_state.login = True
							st.session_state.user = load_user_profile(st.session_state.user)
							pre_load_variables(st.session_state.user['id'])
							load_and_fetch_vectorstore_for_user(st.session_state.user['id'])
							load_bot_settings(st.session_state.user['id'])
							st.rerun()
					with col2:
						pass
				
		
		#Personal Dashboard
		elif st.session_state.option == 'Class Dashboard':
			st.subheader(f":green[{st.session_state.option}]")
			if st.session_state.user['profile_id'] == SA:
				sch_id, msg = process_user_profile(st.session_state.user["profile_id"])
				st.write(msg)
				download_data_table_csv(st.session_state.user["id"], sch_id, st.session_state.user["profile_id"])
			else:
				download_data_table_csv(st.session_state.user["id"], st.session_state.user["school_id"], st.session_state.user["profile_id"])
			display_vectorstores()
			vectorstore_selection_interface(st.session_state.user['id'])
		#Lesson Assistant
		elif st.session_state.option == "Lesson Collaborator":
			st.subheader(f":green[{st.session_state.option}]")	
			prompt = lesson_collaborator()
			if prompt:
				lesson_bot(prompt, st.session_state.lesson_collaborator, LESSON_COLLAB)	
					
		elif st.session_state.option == "Lesson Commentator":
			st.subheader(f":green[{st.session_state.option}]")
			prompt = lesson_commentator()
			if prompt:
				lesson_bot(prompt, st.session_state.lesson_commentator, LESSON_COMMENT)
		
		elif st.session_state.option == "Lesson Designer Map":
			st.subheader(f":green[{st.session_state.option}]")
			lesson_map_generator()

		elif st.session_state.option == "Lesson Design Facilitator (Chatbot)":
			st.subheader(f":green[{st.session_state.option}]")
			choice = sac.buttons([
								sac.ButtonsItem(label='Collaborator Mode', icon='person-hearts',color='green'),
								sac.ButtonsItem(label='Default', icon='person-fill',color='blue'),
								sac.ButtonsItem(label='Commentator Mode', icon='person-plus-fill',color='red'),
							], index=1,format_func='title', align='center', size='small', type='primary')
			sac.divider(label='Chabot Settings', icon='robot', align='center', direction='horizontal', dashed=False, bold=False)

			if choice == "Collaborator Mode":
				st.session_state.chatbot = st.session_state.collaborator_mode
			elif choice == "Default Chatbot": #remove the chatbot template
				st.session_state.chatbot = st.session_state.lesson_default
			elif choice == "Commentator Mode":
				st.session_state.chatbot = st.session_state.commentator_mode
			
			
			#check if API key is entered
			with st.expander("Lesson Designer Settings"):
				vectorstore_selection_interface(st.session_state.user['id'])
				if st.session_state.vs:#chatbot with knowledge base
					raw_search = sac.switch(label='Raw Search', value=False, align='start', position='left')
				clear = sac.switch(label='Clear Chat', value=False, align='start', position='left')
				if clear == True:	
					clear_session_states()
				mem = sac.switch(label='Enable Memory', value=True, align='start', position='left')
				if mem == True:	
					st.session_state.memoryless = False
				else:
					st.session_state.memoryless = True
				rating = sac.switch(label='Rate Response', value=True, align='start', position='left')
				if rating == True:	
					st.session_state.rating = True
				else:
					st.session_state.rating = False
				# vm = sac.switch(label='Visual Mapping', value=False, align='start', position='left', size='small')
				# if vm == True:	
				# 	st.session_state.visuals = True
				# else:
				# 	st.session_state.visuals = False
			if st.session_state.vs:#chatbot with knowledge base
				if raw_search == True:
					search_bot()
				else:
					if st.session_state.memoryless: #memoryless chatbot with knowledge base but no memory
						basebot_qa(LESSON_BOT)
					else:
						basebot_qa_memory(LESSON_BOT) #chatbot with knowledge base and memory
			else:#chatbot with no knowledge base
				if st.session_state.memoryless: #memoryless chatbot with no knowledge base and no memory
					basebot(LESSON_BOT)
				else:
					basebot_memory(LESSON_BOT) #chatbot with no knowledge base but with memory
		elif st.session_state.option == "Prototype Chatbot":
			st.subheader(f":green[{st.session_state.option}]")
			st.write(":blue[Smart Agent Prototype - Available soon in the next release]")
			
		elif st.session_state.option == 'Bot & Prompt Management': #ensure that it is for administrator or super_admin
			if st.session_state.user['profile_id'] == SA or st.session_state.user['profile_id'] == AD:
				st.subheader(f":green[{st.session_state.option}]")
				create_prompt_template(st.session_state.user['id'])
				update_prompt_template(st.session_state.user['profile_id'])
				st.subheader("OpenAI Chatbot Parameters Settings")
				bot_settings_interface(st.session_state.user['profile_id'], st.session_state.user['school_id'])
			else:
				st.subheader(f":red[This option is accessible only to administrators only]")
		
		#Knowledge Base Tools
		elif st.session_state.option == 'Files Management':
			st.subheader(f":green[{st.session_state.option}]") 
			display_files()
			docs_uploader()
			delete_files()

		elif st.session_state.option == "Knowledge Base Editor":
			st.subheader(f":green[{st.session_state.option}]") 
			options = sac.steps(
				items=[
					sac.StepsItem(title='Step 1', description='Create a new knowledge base'),
					sac.StepsItem(title='Step 2', description='Assign a knowledge base to a user'),
					sac.StepsItem(title='Step 3', description='Delete a knowledge base (Optional)'),
				],
				format_func='title',
				placement='vertical',
				size='small'
			)
			if options == "Step 1":
				st.subheader("KB created in the repository")
				display_vectorstores()
				st.subheader("Files available in the repository")
				display_files()
				create_vectorstore()
			elif options == "Step 2":
				st.subheader("KB created in the repository")
				display_vectorstores()
				vectorstore_selection_interface(st.session_state.user['id'])
				link_profiles_to_vectorstore_interface(st.session_state.user['id'])
	
			elif options == "Step 3":
				st.subheader("KB created in the repository")
				display_vectorstores()
				delete_vectorstores()

		#Organisation Tools
		elif st.session_state.option == "Users Management":
			st.subheader(f":green[{st.session_state.option}]") 
			sch_id, msg = process_user_profile(st.session_state.user["profile_id"])
			rows = has_at_least_two_rows()
			if rows >= 2:
				#Password Reset
				st.subheader("User accounts information")
				df = display_accounts(sch_id)
				st.warning("Password Management")
				st.subheader("Reset passwords of users")
				reset_passwords(df)
		
		elif st.session_state.option == "Org Management":
			if st.session_state.user['profile_id'] == SA:
				st.subheader(f":green[{st.session_state.option}]") 
				#direct_vectorstore_function()
				
				if check_password(st.session_state.user["username"], SUPER_PWD):
						st.write("To start creating your teachers account, please change the default password of your administrator account under profile settings")
				else:
					sch_id, msg = process_user_profile(st.session_state.user["profile_id"])
					create_flag = False
					rows = has_at_least_two_rows()
					if rows >= 2:
						create_flag = check_multiple_schools()
					st.markdown("###")
					st.write(msg)
					st.markdown("###")
					steps_options = sac.steps(
								items=[
									sac.StepsItem(title='step 1', description='Create Students and Teachers account of a new school', disabled=create_flag),
									sac.StepsItem(title='step 2', description='Remove/Assign Teachers to Classes'),
									sac.StepsItem(title='step 3', description='Change Teachers Profile'),
									sac.StepsItem(title='step 4', description='Setting function access for profiles'),
									sac.StepsItem(title='step 5', description='Reassign Students to Classes(Optional)'),
									sac.StepsItem(title='step 6', description='Managing SQL Schema Tables',icon='radioactive'),
								], format_func='title', placement='vertical', size='small'
							)
					if steps_options == "step 1":
						if create_flag:
							st.write("School created, click on Step 2")
						else:
							create_org_structure()
					elif steps_options == "step 2":
						remove_or_reassign_teacher_ui(sch_id)
					elif steps_options == "step 3":
						change_teacher_profile_ui(sch_id)
					elif steps_options == "step 4":
						link_users_to_app_function_ui(sch_id)
					elif steps_options == "step 5":
						reassign_student_ui(sch_id)
					elif steps_options == "step 6":
						st.subheader(":red[Managing SQL Schema Tables]")
						st.warning("Please do not use this function unless you know what you are doing")
						if st.checkbox("I know how to manage SQL Tables"):
							st.subheader(":red[Display and Edit Tables - please do so if you have knowledge of the current schema]")
							manage_tables()
							st.subheader(":red[Delete Table - Warning please use this function with extreme caution]")
							delete_tables()
			else:
				st.subheader(f":red[This option is accessible only to super administrators only]")
						
		
		elif st.session_state.option == "Profile Settings":
			st.subheader(f":green[{st.session_state.option}]") 
			#direct_vectorstore_function()
			password_settings(st.session_state.user["username"])

		elif st.session_state.option == 'Application Info':
			st.subheader(f":green[{st.session_state.option}]") 
			st.markdown("Application Information here")
			pass

		elif st.session_state.option == 'Logout':
			for key in st.session_state.keys():
				del st.session_state[key]
			st.rerun()
			pass
	except Exception as e:
		st.exception(e)

if __name__ == "__main__":
	main()