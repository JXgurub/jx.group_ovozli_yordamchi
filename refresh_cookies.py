import getpass
from huggingface_hub import login


def main():
    print("Hugging Face Inference Providers ruxsatiga ega access token kiriting.")
    print("Token yashirin kiritiladi va mahalliy Hugging Face credential store'ida saqlanadi.")
    token = getpass.getpass("Hugging Face token: ").strip()

    if not token.startswith("hf_"):
        print("Token saqlanmadi: Hugging Face access token hf_ bilan boshlanishi kerak.")
        return 1

    try:
        login(token=token, add_to_git_credential=False, skip_if_logged_in=False)
    except Exception as error:
        status_code = getattr(getattr(error, "response", None), "status_code", None)
        if status_code in {401, 403}:
            print("Token rad etildi. Uning amal qilishini va Inference Providers ruxsatini tekshiring.")
        elif status_code:
            print(f"Tokenni tekshirishda HTTP {status_code} xatosi yuz berdi.")
        else:
            print(f"Tokenni saqlab bo'lmadi ({type(error).__name__}); tafsilotlar yashirildi.")
        return 1

    print("Hugging Face tokeni muvaffaqiyatli saqlandi.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())