package com.eeg_server.experiment.oddball;

import com.eeg_server.eegServer.EegData;
import com.eeg_server.experiment.ExperimentType;
import com.eeg_server.utils.TimeUtils;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.File;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.Date;

/**
 * @auter Shiran Schwartz on 20/08/2016.
 */
public class FileUtils {

    private static final Logger logger = LogManager.getLogger(FileUtils.class);
    public static final String NEW_LINE = "\n";
    public static final String CSV_SEPARSATOR = ",";
    private static SimpleDateFormat FILE_FORMAT_NAME = new SimpleDateFormat("yy-MM-dd_HH-mm");

    private static String currFileName = FILE_FORMAT_NAME.format(new Date());

    private static String eegResultsPath = "/Users/shiran/out/";
    private static String path;
    private static Boolean init = false;
    private static final Object sync = new Object();

    private static void init() {
        if (!init) {
            synchronized (sync) {
                if (!init) {
                    path = eegResultsPath + currFileName;
                    boolean created = new File(path).mkdir();
                    if (!created) {
                        logger.error("could not create a new dir:" + path);
                    }
                    init = true;
                }
            }
        }
    }

    public static String getPath() {
        init();
        return path;
    }
    public static void addTypeToPath(ExperimentType type) {
        path = path + type.name() + "/";
    }

    public static Path resolve(String eegData) {
        return Paths.get(path).resolve(eegData);
    }

    public static String formatCsvLine(EegData eegData) {
        StringBuilder builder = new StringBuilder();
        builder.append(TimeUtils.convertOscTimeTagBySpecString(eegData.getTimeTagNtp())); // real timetag
        builder.append(CSV_SEPARSATOR);
        builder.append(TimeUtils.format(eegData.getServerTimeTag()));  // server timetag
        builder.append(CSV_SEPARSATOR);
        builder.append(eegData.getType());// type
        builder.append(CSV_SEPARSATOR);
        builder.append(Arrays.toString(eegData.getArguments())); // data
        builder.append(CSV_SEPARSATOR);
        builder.append(eegData.getServerTimeTag()); // raw timetag
        builder.append(CSV_SEPARSATOR);
        builder.append(eegData.getServerTimeTag());// raw server time
        return builder.toString();
    }
}
