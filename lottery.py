import streamlit as st
import random
import pandas as pd
from io import BytesIO  # 用於導出結果

# 初始化 session_state
if "page" not in st.session_state:
    st.session_state.page = "setup"
if "winners" not in st.session_state:
    st.session_state.winners = []
if "current_prize_index" not in st.session_state:
    st.session_state.current_prize_index = 0
if "prize_ready" not in st.session_state:
    st.session_state.prize_ready = False

# 內定人選與指定加彩獎項的位置
preset_winners = {
    "Tommy加彩5000": (2, "Johnson"),
    "Wayne加彩5000": (4, "Yiyi"),
    "Jamie加彩5000": (1, "Lunar")
}

# 獎項設置
main_prizes = {
    "五等獎": 20,
    "四等獎": 10,
    "三等獎": 6,
    "二等獎": 3,
    "一等獎": 1,
}

bonus_prizes = {
    "Tommy加彩5000": 5,
    "Wayne加彩5000": 5,
    "Jamie加彩5000": 5,
}

# 獎項英文翻譯
prize_translations = {
    "五等獎": "Fifth Prize",
    "四等獎": "Fourth Prize",
    "三等獎": "Third Prize",
    "二等獎": "Second Prize",
    "一等獎": "First Prize",
    "Tommy加彩5000": "Tommy Bonus 5000",
    "Wayne加彩5000": "Wayne Bonus 5000",
    "Jamie加彩5000": "Jamie Bonus 5000",
}

# 將獎項添加英文翻譯
def add_translation(prize_name):
    return f"{prize_name} ({prize_translations.get(prize_name, '')})"

# 抽獎設置畫面
if st.session_state.page == "setup":
    st.title("宿霧場館新年抽獎 🎉")

    # 上傳參加者名單
    uploaded_file = st.file_uploader("請上傳參加者名單 (Excel 檔，需包含 'Name' 欄位)", type=["xlsx"])
    if uploaded_file:
        # 讀取名單
        data = pd.read_excel(uploaded_file)
        if 'Name' not in data.columns:
            st.error("請確保文件包含 'Name' 欄位！")
        else:
            participants = data['Name'].dropna().tolist()  # 去除空值
            # 移除內定人選，確保他們不參與主獎項
            for _, name in preset_winners.values():
                if name in participants:
                    participants.remove(name)

            st.session_state.participants = participants
            st.write(f"已載入名單，共有 {len(participants)} 人")

            # 顯示主獎項分配
            st.subheader("主獎項分配")
            for prize, count in main_prizes.items():
                st.write(f"{add_translation(prize)}: {count} 名")

            # 開始抽獎按鈕
            if st.button("開始抽獎"):
                st.session_state.page = "draw"
                st.session_state.current_prize_index = 0
                st.session_state.prize_ready = False

# 抽獎結果畫面
elif st.session_state.page == "draw":
    participants = st.session_state.participants
    current_prize_index = st.session_state.current_prize_index
    main_prize_names = list(main_prizes.keys())
    bonus_prize_names = list(bonus_prizes.keys())

    # 獲取當前獎項
    all_prizes = main_prize_names + bonus_prize_names
    if current_prize_index < len(all_prizes):
        current_prize = all_prizes[current_prize_index]
        prize_count = main_prizes.get(current_prize, bonus_prizes.get(current_prize, 0))

        # 判斷是否為加彩項目
        is_bonus_prize = current_prize in bonus_prize_names

        # 顯示獎項名稱與人數，等待抽取
        if not st.session_state.prize_ready:
            if is_bonus_prize:
                # 加彩項目標題更大字體
                st.markdown(
                    f"<h1 style='text-align: center; color: blue; font-size: 48px;'>🎁 {add_translation(current_prize)}</h1>",
                    unsafe_allow_html=True,
                )
            else:
                # 主獎項標題
                st.subheader(f"🏆 {add_translation(current_prize)}")

            st.write(f"本次抽取人數：{prize_count} 名")
            if st.button("準備抽取"):
                st.session_state.prize_ready = True
        else:
            # 抽取按鈕
            winners = []
            if st.button("抽取"):
                if len(participants) > 0 and prize_count > 0:
                    # 判斷是否為加彩項目，並將內定人選放入指定位置
                    if is_bonus_prize and current_prize in preset_winners:
                        position, name = preset_winners[current_prize]
                        temp_winners = random.sample(participants, k=min(prize_count, len(participants)))
                        
                        # 確保內定人選插入正確位置
                        position = min(position - 1, len(temp_winners))  # 防止越界
                        temp_winners.insert(position, name)
                        winners = temp_winners

                    else:
                        # 正常隨機抽取
                        winners = random.sample(participants, k=min(prize_count, len(participants)))

                    # 移除已獲獎者
                    participants = [p for p in participants if p not in winners]
                    st.session_state.participants = participants
                    st.session_state.winners.extend([(add_translation(current_prize), winner) for winner in winners])
                    st.session_state.current_prize_index += 1
                    st.session_state.prize_ready = False

                    # 顯示獲獎者
                    st.markdown(
                        f"<h1 style='text-align: center; color: red;'>🎉 {add_translation(current_prize)} 獲獎者</h1>",
                        unsafe_allow_html=True,
                    )
                    for winner in winners:
                        st.success(f"🎉 獲獎者：{winner} 🎉")
                else:
                    st.warning("參加者不足，無法抽取獎項！")
    else:
        # 抽獎完成
        st.title("🎉 抽獎全部完成！")

        # 獲獎名單
        result_df = pd.DataFrame(st.session_state.winners, columns=["獎項", "獲獎者"])
        st.subheader("得獎名單")
        st.write(result_df)

        # 導出結果按鈕
        buffer_winners = BytesIO()
        with pd.ExcelWriter(buffer_winners, engine='openpyxl') as writer:
            result_df.to_excel(writer, index=False, sheet_name="得獎名單")
        st.download_button(
            label="下載得獎名單",
            data=buffer_winners.getvalue(),
            file_name="得獎名單.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        # 返回設置按鈕
        if st.button("返回抽獎設置"):
            st.session_state.page = "setup"
            st.session_state.winners = []
            st.session_state.current_prize_index = 0
            st.session_state.prize_ready = False
