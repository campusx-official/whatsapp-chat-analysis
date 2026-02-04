import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    layout="wide"
)

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
st.sidebar.title("📊 WhatsApp Chat Analyzer")
uploaded_file = st.sidebar.file_uploader(
    "Upload WhatsApp Chat (.txt file)",
    type=["txt"]
)

# --------------------------------------------------
# Main Logic
# --------------------------------------------------
if uploaded_file is not None:
    try:
        with st.spinner("Processing chat data..."):
            bytes_data = uploaded_file.getvalue()
            data = bytes_data.decode("utf-8")
            df = preprocessor.preprocess(data)

        # Fetch unique users
        user_list = df['user'].unique().tolist()
        if 'group_notification' in user_list:
            user_list.remove('group_notification')

        user_list.sort()
        user_list.insert(0, "Overall")

        selected_user = st.sidebar.selectbox(
            "Show analysis with respect to",
            user_list
        )

        if st.sidebar.button("Show Analysis"):

            # --------------------------------------------------
            # Top Statistics
            # --------------------------------------------------
            num_messages, words, num_media_messages, num_links = helper.fetch_stats(
                selected_user, df
            )

            st.title("📌 Top Statistics")
            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Total Messages", num_messages)
            col2.metric("Total Words", words)
            col3.metric("Media Shared", num_media_messages)
            col4.metric("Links Shared", num_links)

            # --------------------------------------------------
            # Monthly Timeline
            # --------------------------------------------------
            st.title("📅 Monthly Timeline")
            timeline = helper.monthly_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(timeline['time'], timeline['message'], color='green')
            plt.xticks(rotation=90)
            st.pyplot(fig)

            # --------------------------------------------------
            # Daily Timeline
            # --------------------------------------------------
            st.title("📆 Daily Timeline")
            daily_timeline = helper.daily_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(
                daily_timeline['only_date'],
                daily_timeline['message'],
                color='black'
            )
            plt.xticks(rotation=90)
            st.pyplot(fig)

            # --------------------------------------------------
            # Activity Maps
            # --------------------------------------------------
            st.title("🗺️ Activity Map")
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Most Busy Day")
                busy_day = helper.week_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_day.index, busy_day.values, color='purple')
                plt.xticks(rotation=90)
                st.pyplot(fig)

            with col2:
                st.subheader("Most Busy Month")
                busy_month = helper.month_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_month.index, busy_month.values, color='orange')
                plt.xticks(rotation=90)
                st.pyplot(fig)

            # --------------------------------------------------
            # Weekly Heatmap
            # --------------------------------------------------
            st.title("🔥 Weekly Activity Heatmap")
            user_heatmap = helper.activity_heatmap(selected_user, df)
            fig, ax = plt.subplots()
            sns.heatmap(user_heatmap, ax=ax)
            st.pyplot(fig)

            # --------------------------------------------------
            # Most Busy Users (Group Level)
            # --------------------------------------------------
            if selected_user == "Overall":
                st.title("👥 Most Busy Users")
                x, new_df = helper.most_busy_users(df)

                col1, col2 = st.columns(2)

                with col1:
                    fig, ax = plt.subplots()
                    ax.bar(x.index, x.values, color='red')
                    plt.xticks(rotation=90)
                    st.pyplot(fig)

                with col2:
                    st.dataframe(new_df)

            # --------------------------------------------------
            # WordCloud
            # --------------------------------------------------
            st.title("☁️ WordCloud")
            df_wc = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            ax.axis("off")
            st.pyplot(fig)

            # --------------------------------------------------
            # Most Common Words
            # --------------------------------------------------
            st.title("📝 Most Common Words")
            most_common_df = helper.most_common_words(selected_user, df)
            fig, ax = plt.subplots()
            ax.barh(most_common_df[0], most_common_df[1])
            st.pyplot(fig)

            # --------------------------------------------------
            # Emoji Analysis
            # --------------------------------------------------
            st.title("😂 Emoji Analysis")
            emoji_df = helper.emoji_helper(selected_user, df)

            col1, col2 = st.columns(2)

            with col1:
                st.dataframe(emoji_df)

            with col2:
                fig, ax = plt.subplots()
                ax.pie(
                    emoji_df[1].head(),
                    labels=emoji_df[0].head(),
                    autopct="%0.2f"
                )
                st.pyplot(fig)

    except Exception as e:
        st.error("⚠️ Something went wrong while processing the file.")
        st.exception(e)
