function result = compute_isen_angle_from_csv(csvFile, angleKey, options)
% compute_isen_angle_from_csv
% Corrected iSen angle extraction helper used for final pattern generation.
%
% This function implements the cleaned version of the final iSen-processing
% workflow. It avoids the older exploratory atan2(X,Y) approach used in early
% comparisons and instead estimates the angle from the selected iSen exported
% component after neutral-window alignment.
%
% Usage
% -----
%   options = struct();
%   options.mode = 'axis_offset';          % P01-P08 final workflow
%   options.fc = 6;
%   options.order = 4;
%   options.neutralWindow = [0.2 1.0];
%   options.analysisWindow = [];
%   options.targetNeutral = 0;
%   options.scale = 1;
%   options.offset = 0;
%   options.pairBase = '';                 % optional manual pair base
%   result = compute_isen_angle_from_csv('P01.csv','elbow_fe',options);
%
% For P09-P10, use:
%   options.mode = 'direct_resultant';
%   options.directColumn = 'ResultantAngle';
%
% Output
% ------
%   result.time       Time vector in seconds.
%   result.angle      Corrected device-defined angular descriptor.
%   result.axisUsed   Selected component ('X','Y', or direct column name).
%   result.fs         Estimated sampling frequency.

arguments
    csvFile (1,1) string
    angleKey (1,1) string
    options.mode (1,1) string = "axis_offset"
    options.fc (1,1) double = 6
    options.order (1,1) double = 4
    options.neutralWindow (1,2) double = [0.2 1.0]
    options.analysisWindow double = []
    options.targetNeutral (1,1) double = 0
    options.scale (1,1) double = 1
    options.offset (1,1) double = 0
    options.pairBase (1,1) string = ""
    options.directColumn (1,1) string = ""
    options.invertSign (1,1) logical = false
end

assert(isfile(csvFile), 'CSV file not found: %s', csvFile);
T = readtable(csvFile, 'VariableNamingRule', 'preserve');
headers = string(T.Properties.VariableNames);

time = extractTimeVector(T, headers);
fs = 1 / mean(diff(time), 'omitnan');
assert(options.fc < fs/2, 'Low-pass cutoff must be below Nyquist frequency.');
[b,a] = butter(options.order, options.fc/(fs/2), 'low');

switch lower(options.mode)
    case "direct_resultant"
        col = options.directColumn;
        if col == ""
            col = findDirectResultantColumn(headers, angleKey);
        end
        assert(ismember(col, headers), 'Direct angle column not found: %s', col);
        rawAngle = T.(col);
        angle = filtfilt(b, a, double(rawAngle(:)));
        axisUsed = char(col);

    case "axis_offset"
        [baseName, xCol, yCol] = selectXYPair(T, headers, angleKey, options.pairBase);
        X = filtfilt(b, a, double(T.(xCol)(:)));
        Y = filtfilt(b, a, double(T.(yCol)(:)));

        neutralIdx = time >= options.neutralWindow(1) & time <= options.neutralWindow(2);
        assert(any(neutralIdx), 'Neutral window has no samples. Check neutralWindow.');

        if isempty(options.analysisWindow)
            analysisWindow = [options.neutralWindow(2), min(options.neutralWindow(2) + 1.5, time(end))];
        else
            analysisWindow = options.analysisWindow;
        end
        analysisIdx = time >= analysisWindow(1) & time <= analysisWindow(2);
        if ~any(analysisIdx), analysisIdx = true(size(time)); end

        rangeX = range(X(analysisIdx), 'omitnan');
        rangeY = range(Y(analysisIdx), 'omitnan');
        if rangeY > rangeX
            selected = Y;
            axisUsed = 'Y';
        else
            selected = X;
            axisUsed = 'X';
        end

        baseline = mean(selected(neutralIdx), 'omitnan');
        signFactor = 1;
        if options.invertSign, signFactor = -1; end

        angle = signFactor * (selected - baseline) + options.targetNeutral;
        angle = filtfilt(b, a, angle);
        angle = options.scale * angle + options.offset;

    otherwise
        error('Unknown mode: %s', options.mode);
end

result = struct();
result.file = csvFile;
result.angleKey = angleKey;
result.time = time;
result.angle = angle(:);
result.axisUsed = axisUsed;
result.fs = fs;
end

function time = extractTimeVector(T, headers)
    candidates = ["Tiempo", "Time", "time", "t"];
    col = "";
    for c = candidates
        if ismember(c, headers)
            col = c; break;
        end
    end
    if col == ""
        col = headers(1);
    end
    time = T.(col);
    if isdatetime(time)
        time = seconds(time - time(1));
    end
    time = double(time(:));
    if max(time) > 1e4
        % Some exports store time in milliseconds.
        time = (time - time(1)) / 1000;
    else
        time = time - time(1);
    end
end

function [baseName, xCol, yCol] = selectXYPair(T, headers, angleKey, pairBase)
    if pairBase ~= ""
        baseName = pairBase;
        xCol = pairBase + "_X";
        yCol = pairBase + "_Y";
        assert(ismember(xCol, headers) && ismember(yCol, headers), 'Manual pairBase not found: %s', pairBase);
        return;
    end

    xCols = headers(endsWith(headers, "_X"));
    bases = erase(xCols, "_X");
    validBases = strings(0);
    for b = bases
        if ismember(b + "_Y", headers)
            validBases(end+1) = b; %#ok<AGROW>
        end
    end
    assert(~isempty(validBases), 'No *_X/*_Y pairs were found.');

    key = lower(angleKey);
    score = zeros(size(validBases));
    for i = 1:numel(validBases)
        bLower = lower(validBases(i));
        if contains(key, "hombro") || contains(key, "shoulder")
            score(i) = score(i) + containsAny(bLower, ["hombro","shoulder","arm","brazo"]);
        end
        if contains(key, "codo") || contains(key, "elbow")
            score(i) = score(i) + containsAny(bLower, ["codo","elbow"]);
        end
        if contains(key, "muneca") || contains(key, "wrist")
            score(i) = score(i) + containsAny(bLower, ["muneca","wrist","mano","hand"]);
        end
        if contains(key, "abd")
            score(i) = score(i) + containsAny(bLower, ["abd","aa"]);
        end
        if contains(key, "fe")
            score(i) = score(i) + containsAny(bLower, ["fe","flex","ext"]);
        end
    end
    [~, idx] = max(score);
    if all(score == 0)
        idx = 1;
        warning('No keyword match for %s. Using first available pair: %s.', angleKey, validBases(idx));
    end
    baseName = validBases(idx);
    xCol = baseName + "_X";
    yCol = baseName + "_Y";
end

function tf = containsAny(textValue, keys)
    tf = false;
    for k = keys
        tf = tf || contains(textValue, k);
    end
end

function col = findDirectResultantColumn(headers, angleKey)
    key = lower(angleKey);
    lowerHeaders = lower(headers);
    candidates = contains(lowerHeaders, "result") | contains(lowerHeaders, "angle") | contains(lowerHeaders, "angulo") | contains(lowerHeaders, key);
    idx = find(candidates, 1, 'first');
    assert(~isempty(idx), 'No direct resultant/angle column found. Provide options.directColumn.');
    col = headers(idx);
end
