import os
import re
import time
import base64
import streamlit as st

from appreviews import init_app_crew

st.set_page_config(initial_sidebar_state="expanded")

robot_icon = """
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<!-- Uploaded to: SVG Repo, www.svgrepo.com, Transformed by: SVG Repo Mixer Tools -->
<svg fill="#000000" height="64px" width="64px" version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 508 508" xml:space="preserve">
<g id="SVGRepo_bgCarrier" stroke-width="0"/>
<g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"/>
<g id="SVGRepo_iconCarrier"> <g> <g> <path d="M190.838,331.684c-9.708,0-17.604,7.892-17.604,17.6c0,9.7,7.896,17.596,17.604,17.596 c9.704,0,17.596-7.896,17.592-17.596C208.43,339.58,200.538,331.684,190.838,331.684z M190.838,358.876 c-5.296,0-9.604-4.304-9.604-9.596s4.308-9.6,9.604-9.6c5.292,0,9.592,4.308,9.592,9.6 C200.43,354.572,196.126,358.876,190.838,358.876z"/> </g> </g> <g> <g> <path d="M353.138,75.4H155.194c-15.292,0-28.208,12.808-28.208,27.972v39.352c0,14.86,11.892,29.712,26.516,33.112l76.744,17.792 c6.456,1.504,15.016,2.328,24.1,2.328c9.132,0,17.732-0.832,24.224-2.348l76.108-17.756c14.524-3.388,26.34-18.248,26.34-33.128 v-39.352C381.018,87.948,368.51,75.4,353.138,75.4z M373.014,142.724c0,11.184-9.236,22.788-20.16,25.34L276.75,185.82 c-5.824,1.36-13.992,2.136-22.404,2.136c-8.492,0-16.408-0.748-22.292-2.12l-76.744-17.792 c-11.02-2.564-20.328-14.156-20.328-25.32v-39.352c0-10.828,9.252-19.972,20.208-19.972c0,0,197.944,0,197.944,0 c10.964,0,19.88,8.96,19.88,19.972V142.724z"/> </g> </g> <g> <g> <path d="M270.058,0h-31.684c-24.22,0-43.928,19.6-43.928,43.684V79.4c0,2.212,1.792,4,4,4s4-1.788,4-4V43.684 C202.446,24.008,218.562,8,238.374,8h31.684c19.572,0,35.496,16.008,35.496,35.684V79.4c0,2.212,1.792,4,4,4s4-1.792,4-4V43.684 C313.554,19.596,294.042,0,270.058,0z"/> </g> </g> <g> <g> <path d="M202.93,388.892h-24.188c-24.164,0-43.824,19.596-43.824,43.68v51.588c0,2.212,1.792,4,4,4s4-1.788,4-4v-51.588 c0-19.676,16.072-35.68,35.824-35.68h24.188c19.388,0,35.164,16.004,35.164,35.68v51.588c0,2.212,1.792,4,4,4s4-1.788,4-4v-51.588 C246.094,408.484,226.73,388.892,202.93,388.892z"/> </g> </g> <g> <g> <path d="M190.506,178.572c-2.208,0-4,1.788-4,4v63.492c0,2.212,1.792,4,4,4s4-1.792,4-4v-63.492 C194.506,180.36,192.714,178.572,190.506,178.572z"/> </g> </g> <g> <g> <path d="M317.49,178.572c-2.208,0-4,1.788-4,4v63.492c0,2.212,1.792,4,4,4s4-1.792,4-4v-63.492 C321.49,180.36,319.698,178.572,317.49,178.572z"/> </g> </g> <g> <g> <path d="M226.222,242.06h-35.404c-19.576,0-35.5,16.036-35.5,35.748c0,19.712,15.924,35.748,35.5,35.748h35.404 c2.208,0,4-1.792,4-4.004V246.06C230.222,243.848,228.43,242.06,226.222,242.06z M222.222,305.56h-31.404 c-15.164,0-27.5-12.444-27.5-27.748c0-15.304,12.336-27.748,27.5-27.748h31.404V305.56z"/> </g> </g> <g> <g> <path d="M130.982,146.824h-29.8c-11.928,0-21.632-9.776-21.632-21.792s9.704-21.792,21.632-21.792h29.8c2.208,0,4-1.788,4-4 c0-2.212-1.792-4-4-4h-29.8c-16.34,0-29.632,13.364-29.632,29.792c0,16.428,13.296,29.792,29.632,29.792h29.8c2.208,0,4-1.788,4-4 C134.982,148.612,133.19,146.824,130.982,146.824z"/> </g> </g> <g> <g> <path d="M317.406,242.064h-35.628c-2.208,0-4,1.788-4,4v63.492c0,2.212,1.792,4,4,4h35.628c19.572,0,35.5-16.032,35.5-35.744 C352.906,258.1,336.982,242.064,317.406,242.064z M317.402,305.556h-31.628V250.06h31.628c15.164,0,27.5,12.444,27.5,27.748 C344.902,293.112,332.566,305.556,317.402,305.556z"/> </g> </g> <g> <g> <path d="M281.778,261.908h-55.556c-2.208,0-4,1.788-4,4v23.808c0,2.212,1.792,4,4,4h55.552c2.212,0,4-1.792,4.004-4v-23.808 C285.778,263.696,283.986,261.908,281.778,261.908z M277.778,285.716h-47.556v-15.808h47.556V285.716z"/> </g> </g> <g> <g> <path d="M198.442,357.144c-2.208,0-4,1.788-4,4v27.748c0,2.212,1.792,4,4,4c2.212,0,4-1.792,4-4v-27.748 C202.442,358.932,200.65,357.144,198.442,357.144z"/> </g> </g> <g> <g> <path d="M182.57,357.144c-2.208,0-4,1.788-4,4v27.748c0,2.212,1.792,4,4,4s4-1.792,4-4v-27.748 C186.57,358.932,184.778,357.144,182.57,357.144z"/> </g> </g> <g> <g> <path d="M198.442,305.556c-2.208,0-4,1.788-4,4v27.776c0,2.212,1.792,4,4,4c2.212,0,4-1.788,4-4v-27.776 C202.442,307.344,200.65,305.556,198.442,305.556z"/> </g> </g> <g> <g> <path d="M182.57,305.556c-2.208,0-4,1.788-4,4v27.776c0,2.212,1.792,4,4,4s4-1.788,4-4v-27.776 C186.57,307.344,184.778,305.556,182.57,305.556z"/> </g> </g> <g> <g> <path d="M111.142,146.824c-2.208,0-4,1.788-4,4v35.716c0,2.212,1.792,4,4,4s4-1.788,4-4v-35.716 C115.142,148.612,113.35,146.824,111.142,146.824z"/> </g> </g> <g> <g> <path d="M95.266,146.824c-2.208,0-4,1.788-4,4v35.716c0,2.212,1.792,4,4,4c2.212,0,4-1.788,4-4v-35.716 C99.266,148.612,97.474,146.824,95.266,146.824z"/> </g> </g> <g> <g> <path d="M246.066,480.16h-11.908c-2.208,0-4,1.788-4,4c0,2.212,1.792,4,4,4h7.904V500H138.95v-11.84h63.46c2.208,0,4-1.788,4-4 c0-2.212-1.792-4-4-4h-67.46c-2.208,0-4,1.788-4,4V504c0,2.212,1.792,4,4,4h111.112c2.208,0,4-1.788,4.004-4v-19.84 C250.066,481.948,248.274,480.16,246.066,480.16z"/> </g> </g> <g> <g> <path d="M317.49,331.684c-9.704,0-17.6,7.892-17.6,17.6c0,9.7,7.896,17.596,17.6,17.596c9.704,0,17.6-7.896,17.6-17.596 C335.09,339.58,327.194,331.684,317.49,331.684z M317.49,358.876c-5.292,0-9.6-4.304-9.6-9.596s4.304-9.6,9.6-9.6 c5.296,0,9.6,4.308,9.6,9.6C327.09,354.572,322.782,358.876,317.49,358.876z"/> </g> </g> <g> <g> <path d="M329.586,388.892h-24.188c-23.984,0-43.492,19.596-43.492,43.68v51.588c0,2.212,1.792,4,4,4s4-1.788,4-4v-51.588 c0-19.676,15.92-35.68,35.492-35.68h24.188c19.572,0,35.492,16.004,35.492,35.68v51.588c0,2.212,1.792,4,4,4s4-1.788,4-4v-51.588 C373.078,408.484,353.57,388.892,329.586,388.892z"/> </g> </g> <g> <g> <path d="M325.426,357.144c-2.208,0-4,1.788-4,4v27.748c0,2.212,1.792,4,4,4c2.212,0,4-1.792,4-4v-27.748 C329.426,358.932,327.634,357.144,325.426,357.144z"/> </g> </g> <g> <g> <path d="M309.554,357.144c-2.208,0-4,1.788-4,4v27.748c0,2.212,1.792,4,4,4s4-1.792,4-4v-27.748 C313.554,358.932,311.762,357.144,309.554,357.144z"/> </g> </g> <g> <g> <path d="M325.426,305.556c-2.208,0-4,1.788-4,4v27.776c0,2.212,1.792,4,4,4c2.212,0,4-1.788,4-4v-27.776 C329.426,307.344,327.634,305.556,325.426,305.556z"/> </g> </g> <g> <g> <path d="M309.554,305.556c-2.208,0-4,1.788-4,4v27.776c0,2.212,1.792,4,4,4s4-1.788,4-4v-27.776 C313.554,307.344,311.762,305.556,309.554,305.556z"/> </g> </g> <g> <g> <path d="M373.042,480.16h-11.904c-2.208,0-4,1.788-4,4c0,2.212,1.792,4,4,4h7.904V500H265.934v-11.84h63.464c2.208,0,4-1.788,4-4 c0-2.212-1.792-4-4-4h-67.464c-2.208,0-4,1.788-4,4V504c0,2.212,1.792,4,4,4h111.112c2.208,0,4-1.788,3.996-4v-19.84 C377.042,481.948,375.25,480.16,373.042,480.16z"/> </g> </g> <g> <g> <path d="M115.11,182.54H91.238c-15.3,0-27.748,12.476-27.748,27.808v75.4c0,2.212,1.792,4,4,4h71.428c2.208,0,4-1.792,4-4v-75.4 C142.918,195.016,130.442,182.54,115.11,182.54z M134.918,281.748H71.49v-71.4c0-10.92,8.86-19.808,19.748-19.808h23.872 c10.92,0,19.808,8.888,19.808,19.808V281.748z"/> </g> </g> <g> <g> <path d="M138.918,230.16h-7.936c-2.208,0-4,1.788-4,4c0,2.212,1.792,4,4,4h7.936c2.208,0,4-1.788,4-4 C142.918,231.948,141.126,230.16,138.918,230.16z"/> </g> </g> <g> <g> <path d="M107.17,230.16H67.49c-2.208,0-4,1.788-4,4c0,2.212,1.792,4,4,4h39.68c2.212,0,4-1.788,4-4 C111.17,231.948,109.378,230.16,107.17,230.16z"/> </g> </g> <g> <g> <path d="M138.918,265.872H67.49c-2.208,0-4,1.788-4,4c0,2.212,1.792,4,4,4h71.428c2.208,0,4-1.788,4-4 C142.918,267.66,141.126,265.872,138.918,265.872z"/> </g> </g> <g> <g> <path d="M406.426,95.24H377.01c-2.208,0-4,1.788-4,4c0,2.212,1.792,4,4,4h29.416c11.92,0,21.62,9.776,21.62,21.792 s-9.7,21.792-21.62,21.792H377.01c-2.208,0-4,1.788-4,4c0,2.212,1.792,4,4,4h29.416c16.336,0,29.62-13.364,29.62-29.792 C436.046,108.604,422.758,95.24,406.426,95.24z"/> </g> </g> <g> <g> <path d="M396.854,146.824c-2.208,0-4,1.788-4,4v35.716c0,2.212,1.792,4,4,4s4-1.788,4-4v-35.716 C400.854,148.612,399.062,146.824,396.854,146.824z"/> </g> </g> <g> <g> <path d="M412.73,146.824c-2.208,0-4,1.788-4,4v35.716c0,2.212,1.792,4,4,4s4-1.788,4-4v-35.716 C416.73,148.612,414.938,146.824,412.73,146.824z"/> </g> </g> <g> <g> <path d="M416.366,182.54h-23.872c-15.116,0-27.416,12.476-27.416,27.808v75.4c0,2.212,1.792,4,4,4h71.428c2.208,0,4-1.792,4.004-4 v-75.4C444.51,195.016,431.886,182.54,416.366,182.54z M436.506,281.748h-63.428h-0.004v-71.4c0-10.92,8.712-19.808,19.416-19.808 h23.872c10.92,0,20.144,9.068,20.144,19.808V281.748z"/> </g> </g> <g> <g> <path d="M377.014,230.16h-7.936c-2.208,0-4,1.788-4,4c0,2.212,1.792,4,4,4h7.936c2.208,0,4-1.788,4-4 C381.014,231.948,379.222,230.16,377.014,230.16z"/> </g> </g> <g> <g> <path d="M440.506,230.16h-39.684c-2.208,0-4,1.788-4,4c0,2.212,1.792,4,4,4h39.684c2.208,0,4-1.788,4-4 C444.506,231.948,442.714,230.16,440.506,230.16z"/> </g> </g> <g> <g> <path d="M440.506,265.872h-71.428c-2.208,0-4,1.788-4,4c0,2.212,1.792,4,4,4h71.428c2.208,0,4-1.788,4-4 C444.506,267.66,442.714,265.872,440.506,265.872z"/> </g> </g> <g> <g> <path d="M254.162,103.984c-17.52,0-31.776,14.252-31.776,31.776c0,17.524,14.256,31.776,31.776,31.776s31.78-14.252,31.78-31.776 C285.942,118.236,271.686,103.984,254.162,103.984z M254.162,159.532c-13.108,0-23.776-10.668-23.776-23.776 s10.664-23.776,23.776-23.776c13.108,0,23.78,10.668,23.78,23.776C277.942,148.864,267.27,159.532,254.162,159.532z"/> </g> </g> <g> <g> <path d="M289.71,39.684h-71.428c-2.208,0-4,1.788-4,4c0,2.212,1.792,4,4,4h71.432c2.208,0,3.996-1.788,3.996-4 C293.71,41.472,291.918,39.684,289.71,39.684z"/> </g> </g> </g>
</svg>
"""

upload_dir = "./upload"


file_ = open("./static/bedrock.jpeg", "rb")
contents = file_.read()
data_url = base64.b64encode(contents).decode("utf-8")
file_.close()



class StreamToExpander:
    def __init__(self, expander):
        self.expander = expander
        self.buffer = []

    def write(self, data):
        # Filter out ANSI escape codes using a regular expression
        cleaned_data = re.sub(r'\x1B\[[0-9;]*[mK]', '', data)
        self.buffer.append(cleaned_data)
        if "\n" in data:
            self.expander.markdown(''.join(self.buffer))
            self.buffer = []

    def flush(self):
        # This flush method is needed for compatibility with sys.stdout
        pass


#processing status
if 'processing' not in st.session_state:
    st.session_state['processing'] = False
    

# Title of the app
st.markdown(f'<h1 style="display: flex; align-items: center;"><span style="font-size: 32px; margin-right: 10px;">{robot_icon}</span> Analysis Agent</h1>', unsafe_allow_html=True)


warning_placeholder = st.empty()
uploaded_file_name =""

def hide_warning():
    time.sleep(2)
    warning_placeholder.empty()


with st.sidebar:
        st.header("App Store Option")

        # Define the options
        options = ['Google Play', 'Apple Store', 'Custom File']

        # Create the selectbox
        selected_store_option = st.selectbox('Select store', options,disabled=st.session_state['processing'])

        st.write(selected_store_option)

        if selected_store_option=="Custom File":
            uploaded_file = st.file_uploader("Custom Data File")
            if uploaded_file is not None:
                # Process the uploaded file
                file_details = {
                    "filename": uploaded_file.name,
                    "filetype": uploaded_file.type,
                    "filesize": uploaded_file.size
                }
                
                #st.write(file_details)
                # get uploaded file name
                uploaded_file_name=uploaded_file.name
                file_path = os.path.join(upload_dir, uploaded_file.name)
                # save file
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        else:
            pass

        country_options = ['USA', 'Singapore', 'Japanese','Korea']
        country_options_key = {"USA":"us", "Singapore":"sg", "Japanese":"jp","Korea":"kr"}
        country_lable=st.selectbox('Select Country', country_options)
        app_name = st.text_input("Enter app name", "",disabled=st.session_state['processing'])

        ranks_options = ['ALL', '5', '4', '3','2','1']
        selected_ranks_option = st.selectbox('Select Ranks', ranks_options,disabled=st.session_state['processing'])

        
        submitted = st.button("Submit")
        
        st.divider()

        st.sidebar.markdown(
                f"""<center><a href="https://aws.amazon.com/bedrock" target="_blank">
            <img src="data:image/jpeg;base64,{data_url}" alt="bedrock logo" style="width:50px;">
            </a><a href="https://github.com/joaomdmoura/crewAI" target="_blank">
                <img src="https://raw.githubusercontent.com/joaomdmoura/crewAI/main/docs/crewai_logo.png" alt="CrewAI Logo" style="width:100px;"/>
            </a></center>
            """,
                unsafe_allow_html=True
            )
            
# Create the analysis_complete_placeholder before it's used
analysis_complete_placeholder = st.container()

if submitted:
    # Display the name
    app_name=app_name.strip()
    if app_name=="" and selected_store_option=="Custom File":
        st.warning("You need input app name.")
        hide_warning()
    

    if app_name!="":
        analysis_complete_placeholder.empty()
        country="us"
        if country_lable in country_options_key:
            country=country_options_key[country_lable]
        
        #st.session_state['processing'] = True
        st.write(f"App name: {app_name},Store: {selected_store_option},Country: {country}, Ranks: [{selected_ranks_option}]")
        expander = st.expander("Processing...")
        
        with expander:
            # Create an instance of the StreamToExpander for directing output to the expander
            stream_to_expander = StreamToExpander(expander)
            # Initialize your CrewAI with the output stream
            rank = -1 
            if selected_ranks_option!="ALL":
                rank = int(selected_ranks_option)
            if (selected_store_option == "Custom File"):
                app_id,crew = init_app_crew(selected_store_option,app_name,country,rank,file=uploaded_file_name,output_stream=stream_to_expander)
            else:
                app_id,crew = init_app_crew( selected_store_option,app_name,country,rank,output_stream=stream_to_expander)

            with st.spinner('Analyzing...'):
                try:
                    # Assuming kickoff method returns a string or an object that can be converted to string
                    crew_result = crew.kickoff()
                except Exception as e:
                    st.error(f"An error occurred during analysis: {e}")
        
        analysis_complete_placeholder = st.container()
        
        with analysis_complete_placeholder:
            st.success('Analysis complete!')
            st.markdown("### Analysis Result", unsafe_allow_html=True)

            # Create an expander
            with st.expander("Show Analysis Result") :
                # Assuming crew_result is a string. If it's not, you might need to convert or format it accordingly.
                if crew_result.startswith("```"):
                    crew_result = crew_result[3:]
                st.markdown(f"{crew_result}", unsafe_allow_html=True)

            
            b64 = base64.b64encode(crew_result.encode("utf-8")).decode()
            md = f'<a href="data:text/markdown;base64,{b64}" download="{app_name}_report.md">Download {app_name} Report</a>'
            st.markdown(md, unsafe_allow_html=True)

            st.session_state['processing'] = False


            with open(f"output/{app_id}.json", "rb") as file:
                file_data = file.read()
                b64 = base64.b64encode(file_data).decode()
                md = f'<a href="data:application/json;base64,{b64}" download="{app_name}.json">Download {app_name} Reviews Data</a>'
                st.markdown(md, unsafe_allow_html=True)

            
    

