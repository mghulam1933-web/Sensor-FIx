import cv2
import mediapipe as mp
import math
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.6, min_tracking_confidence=0.6)
mp_draw = mp.solutions.drawing_utils

# ─────────────────────────────────────────────
# Fungsi hitung jumlah jari
# ─────────────────────────────────────────────
def count_fingers(hand):
    tips = [4, 8, 12, 16, 20]
    fingers = []

    # Jempol
    if hand.landmark[4].x < hand.landmark[3].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # 4 jari lain
    for tip in [8, 12, 16, 20]:
        if hand.landmark[tip].y < hand.landmark[tip - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return sum(fingers)

# ─────────────────────────────────────────────
# Fungsi jarak (untuk PUSH / PULL)
# ─────────────────────────────────────────────
def distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)

# ─────────────────────────────────────────────
# Main Program
# ─────────────────────────────────────────────
cap = cv2.VideoCapture(0)

prev_x = None
prev_z = None
gesture = ""
last_print = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

        # Hitung jari
        fingers = count_fingers(hand)

        # Koordinat telapak tangan
        cx = hand.landmark[9].x
        cy = hand.landmark[9].y

        # Jarak jari tengah ke pergelangan (untuk push/pull)
        z = distance(hand.landmark[0], hand.landmark[9])

        # Default: kosong
        gesture = ""

        # ─────────────────────────────────────────────
        # 1. LIKE 👍 (jempol up)
        # ─────────────────────────────────────────────
        if fingers == 1 and hand.landmark[4].y < hand.landmark[3].y:
            gesture = "👍 LIKE / JEMPOL KE ATAS"

        # ─────────────────────────────────────────────
        # 2. DISLIKE 👎 (jempol down)
        # ─────────────────────────────────────────────
        elif fingers == 1 and hand.landmark[4].y > hand.landmark[3].y:
            gesture = "👎 DISLIKE / JEMPOL KE BAWAH"

        # ─────────────────────────────────────────────
        # 3. GENGGAM ✊
        # ─────────────────────────────────────────────
        elif fingers == 0:
            gesture = "✊ GENGGAM"

        # ─────────────────────────────────────────────
        # 4. LIMA JARI 🖐
        # ─────────────────────────────────────────────
        elif fingers == 5:
            gesture = "🖐 LIMA JARI"

        # ─────────────────────────────────────────────
        # 5. TELUNJUK 👉 (hanya jari 8)
        # ─────────────────────────────────────────────
        elif fingers == 1 and hand.landmark[8].y < hand.landmark[6].y:
            gesture = "👉 TELUNJUK"

        # ─────────────────────────────────────────────
        # 6. SWIPE (gerakan kiri/kanan)
        # ─────────────────────────────────────────────
        if prev_x is not None:
            move_x = cx - prev_x
            if move_x > 0.07:
                gesture = "➡ SWIPE KANAN"
            elif move_x < -0.07:
                gesture = "⬅ SWIPE KIRI"

        prev_x = cx

        # ─────────────────────────────────────────────
        # 7. PUSH / PULL (gerakan maju/mundur)
        # ─────────────────────────────────────────────
        if prev_z is not None:
            move_z = z - prev_z
            if move_z > 0.05:
                gesture = "⬆ PUSH (Tangan Maju)"
            elif move_z < -0.05:
                gesture = "⬇ PULL (Tangan Mundur)"

        prev_z = z

        # ─────────────────────────────────────────────
        # Tampilkan Gesture (memfilter spam)
        # ─────────────────────────────────────────────
        if time.time() - last_print > 0.2:
            cv2.putText(frame, f"Gesture: {gesture}", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            last_print = time.time()
    else:
        gesture = ""

    cv2.imshow("Advanced Hand Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
