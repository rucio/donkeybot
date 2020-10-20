import subprocess


def main():
    subprocess.run(
        f"python -m bot.faq.gui",
        shell=True,
    )


if __name__ == "__main__":
    main()
