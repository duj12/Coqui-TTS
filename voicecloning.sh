#!/usr/bin/env bash

stage=$1

if [ $stage -eq 1 ]; then
OMP_NUM_THREADS=4  python3 -u ./run_tts.py \
  -s  /data/megastore/SHARE/TTS/VoiceClone1/RefSpeaker/spk2utt  \
  -r  /data/megastore/SHARE/TTS/VoiceClone1/RefSpeaker/wav.scp  \
  -t  /data/megastore/SHARE/TTS/VoiceClone1/TextScript/en/CoquiTTS_Text0.txt \
  -l  en  \
  -o  /data/megastore/SHARE/TTS/VoiceClone1/CoquiTTS/en  \
  -g  0,1,2,3,4,5 \
  -n  5
fi

if [ $stage -eq 2 ]; then
OMP_NUM_THREADS=4  python3 -u ./run_tts.py \
  -s  /data/megastore/SHARE/TTS/VoiceClone1/RefSpeaker/spk2utt  \
  -r  /data/megastore/SHARE/TTS/VoiceClone1/RefSpeaker/wav.scp  \
  -t  /data/megastore/SHARE/TTS/VoiceClone1/TextScript/cn/CoquiTTS_Text0.txt \
  -l  zh  \
  -o  /data/megastore/SHARE/TTS/VoiceClone1/CoquiTTS/cn  \
  -g  0,1,2,3,4,5,6,7 \
  -n  5
fi


if [ $stage -eq 3 ]; then
OMP_NUM_THREADS=4  python3 -u ./run_tts.py \
  -s  /data/megastore/SHARE/TTS/VoiceClone1/RefSpeaker1/spk2utt  \
  -d  /data/megastore/SHARE/TTS/VoiceClone1/RefSpeaker1/wav2dur  \
  -r  /data/megastore/SHARE/TTS/VoiceClone1/RefSpeaker1/wav.scp  \
  -t  /data/megastore/SHARE/TTS/VoiceClone1/TextScript/en/CoquiTTS_Text1.txt \
  -l  en  \
  -o  /data/megastore/SHARE/TTS/VoiceClone1/CoquiTTS1/en  \
  -g  0,1,2,3,4,5,6,7 \
  -n  5
fi

if [ $stage -eq 4 ]; then
OMP_NUM_THREADS=4  python3 -u ./run_tts.py \
  -s  /data/megastore/SHARE/TTS/VoiceClone1/RefSpeaker1/spk2utt  \
  -d  /data/megastore/SHARE/TTS/VoiceClone1/RefSpeaker1/wav2dur  \
  -r  /data/megastore/SHARE/TTS/VoiceClone1/RefSpeaker1/wav.scp  \
  -t  /data/megastore/SHARE/TTS/VoiceClone1/TextScript/cn/CoquiTTS_Text1.txt \
  -l  zh  \
  -o  /data/megastore/SHARE/TTS/VoiceClone1/CoquiTTS1/cn  \
  -g  0,1,2,3,4,5,6,7 \
  -n  5
fi
