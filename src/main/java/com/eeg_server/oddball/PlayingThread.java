package com.eeg_server.oddball;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import javax.sound.sampled.LineListener;
import java.util.concurrent.CountDownLatch;

import static com.eeg_server.oddball.Helpers.playSound;

/**
 * @auter shiran on 20/08/2016.
 */
class PlayingThread extends Thread {
    private static final Logger logger = LogManager.getLogger(PlayingThread.class);
    private static final String BEEP_5 = "124905__greencouch__beeps-5.wav";
    private static final String BEEP_1 = "194283__datwilightz__beep-1.wav";

    private static CountDownLatch waitNext;
    private static int counter = 0;
    private static final int NumIterations = 2;

    public PlayingThread() {
    }

    public void run() {
        while (counter < NumIterations) {
            waitNext = new CountDownLatch(1);
            logger.info("playing:" + counter);
            EventListener lineListener = new EventListener(waitNext);
            playSound(BEEP_1, lineListener);
            waitNext();
            counter++;
        }
        OddBallExperiment.isFinished = true;
    }

    private void waitNext() {
        try {
            logger.info("count:" + waitNext.getCount());
            waitNext.await();
            logger.info("count:" + waitNext.getCount());
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}
