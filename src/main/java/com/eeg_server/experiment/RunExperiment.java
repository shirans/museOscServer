package com.eeg_server.experiment;

import com.eeg_server.eegServer.EegServer;
import com.eeg_server.eegServer.MuseEegServer;
import com.eeg_server.experiment.alpha.AlphaWave;
import com.eeg_server.experiment.oddball.OddBallExperiment;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.IOException;


/**
 * @author shiran on 13/08/2016.
 */
public class RunExperiment {

    private static final Logger logger = LogManager.getLogger(RunExperiment.class);

    private static ExperimentType experimentType = ExperimentType.OddBall;

    public static void main(String args[]) throws InterruptedException, IOException {
        System.setProperty("java.awt.headless", "true");
        EegServer server = new MuseEegServer();
        Experiment experiment;
        if (ExperimentType.OddBall.equals(experimentType)) {
            experiment = new OddBallExperiment(10,0, 10,6);
        } else {
            experiment = new AlphaWave(10);
        }
        server.startRecord();
        experiment.start();
        while (!experiment.isFinished()) {
            logger.info("num sound events:" + experiment.getEventsSize());
            logger.info("eeg messages:" + server.getEventsSize());
            Thread.sleep(2000);
        }
        server.stopRecord();
        Thread.sleep(2000);
        experiment.dumpResults();
        server.dumpResults(experimentType.name());
        server.close();
    }
}