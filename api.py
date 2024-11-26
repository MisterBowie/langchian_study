from openai import OpenAI

if __name__ == '__main__':
    client = OpenAI(
        # openai系列的sdk，包括langchain，都需要这个/v1的后缀
        base_url='https://api.openai-proxy.org/v1',
        api_key='sk-M2NQLaQ3rDPK16EEGBi5QfUivICizJ641qh6B7elXulzJuUS',
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Say hi",
            }
        ],
        model="gpt-4o-mini",
    )

    print(chat_completion)