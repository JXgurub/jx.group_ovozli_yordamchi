import multiprocessing
import sys

# Jarvis-ni ishga tushirish
def startJarvis():
    """Process 1: Jarvis asosiy dasturi"""
    try:
        print("Process 1 is running - Starting Jarvis")
        from main import start
        start()
    except Exception as e:
        print(f"Error in startJarvis: {e}")
        import traceback
        traceback.print_exc()
        raise

# Hotword listener-ni ishga tushirish
def listenHotword():
    """Process 2: Hotword listener"""
    try:
        print("Process 2 is running - Listening for hotword")
        from engine.features import hotword
        hotword()
    except Exception as e:
        print(f"Error in listenHotword: {e}")
        import traceback
        traceback.print_exc()


def stop_process(process):
    if not process.is_alive():
        return

    print(f"Terminating {process.name}...")
    process.terminate()
    process.join(timeout=5)
    if process.is_alive():
        process.kill()
        process.join()


# Ikkala processni ishga tushirish
if __name__ == '__main__':
    p1 = multiprocessing.Process(target=startJarvis, name="Jarvis-Main")
    p2 = multiprocessing.Process(target=listenHotword, name="Hotword-Listener")
    interrupted = False

    try:
        p1.start()
        p2.start()
        p1.join()
    except KeyboardInterrupt:
        print("\nInterrupt received. Shutting down...")
        interrupted = True
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        stop_process(p1)
        stop_process(p2)

    if interrupted:
        sys.exit(130)
    if p1.exitcode:
        print(f"System stopped with errors (Jarvis exit code: {p1.exitcode})")
        sys.exit(p1.exitcode)
    print("System stopped successfully")
