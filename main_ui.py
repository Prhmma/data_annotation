from datetime import datetime
import streamlit as st
import pandas as pd
from mongo import MongoDB

class StreamlitUI:
    def __init__(self, mongo_connection):
        self.mongo = mongo_connection

    def get_random_document(self):
        self.document = self.mongo.get_random_document()
        self.original_text = self.document.get("summary", "No text data found in the document.")
        st.session_state.document = self.document
        st.session_state.original_text = self.original_text
        st.session_state.edited_text = self.original_text

    def display_table(self):
        st.header("infobox")
        if "infobox" in self.document:
            infobox = self.document["infobox"]
            df = pd.DataFrame(list(infobox.items()), columns=['Attribute', 'Value'])
            st.dataframe(df)
        else:
            st.write("No table data found in the document.")

    def display_editable_text(self):
        st.header("Summary")
        st.session_state.edited_text = st.text_area(
            "Edit Text", 
            value=st.session_state.get('edited_text', ''), 
            height=300
        )

    def display_history(self):
        st.header("History")
        history = self.mongo.get_history(st.session_state.document["_id"])
        if history:
            history_text = "\n\n".join(history)
            st.text_area("History", value=history_text, height=200, disabled=True)
        else:
            st.text_area("History", value="No history available.", height=200, disabled=True)

    def save_changes(self):
        edited_text = st.session_state.edited_text
        if st.session_state.document:
            if edited_text != st.session_state.original_text:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_history_item = f"{current_time}: {edited_text}"

                self.mongo.append_to_history(st.session_state.document["_id"], new_history_item)

                st.success("Changes saved successfully!")
            else:
                st.info("No changes detected. Nothing was saved.")
        else:
            st.error("No document loaded. Please try again.")
        st.rerun()

    def run(self):
        st.title("MongoDB Document Viewer")

        if 'document' not in st.session_state:
            self.get_random_document()
        else:
            self.document = st.session_state.document
            self.original_text = st.session_state.original_text

        col1, col2 = st.columns(2)

        with col1:
            self.display_table()

        with col2:
            self.display_editable_text()

        self.display_history()

        button_col1, button_col2 = st.columns(2)

        with button_col1:
            if st.button("Save Changes"):
                self.save_changes()

        with button_col2:
            if st.button("Skip"):
                self.skip_to_next()

    def skip_to_next(self):
        self.get_random_document()

if __name__ == "__main__":
    try:
        mongo_connection = MongoDB(
            "mongodb://localhost:27017/",
            "local",
            "data"
        )
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.stop()

    ui = StreamlitUI(mongo_connection)
    ui.run()

    mongo_connection.close_connection()
