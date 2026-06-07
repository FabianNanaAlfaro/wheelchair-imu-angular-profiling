%% codigo_fin_clean.m
% Corrected final iSen pattern extraction workflow.
%
% Purpose
% -------
% This script computes the final device-defined iSen angular descriptors used
% for propulsion-pattern inspection. It replaces the older exploratory atan2
% X/Y angle calculation with the corrected neutral-window and component-based
% procedure implemented in compute_isen_angle_from_csv.m.
%
% Participant-specific rule
% -------------------------
% - P01-P08: use mode = 'axis_offset'.
% - P09-P10: use mode = 'direct_resultant' when the resultant angle is already
%   available in the iSen export.
%
% Manual pattern separation was performed after this step by visual inspection
% of the corrected iSen signals and synchronized video support.

clear; clc; close all;

%% ================= USER SETTINGS =================
participantID = "P08";
rawCsvFile = "../data/raw_isen/P08.csv";  % Edit this path locally.
outputFolder = fullfile(pwd, '..', 'outputs', 'isen_patterns');
if ~exist(outputFolder, 'dir'), mkdir(outputFolder); end

% Final descriptors to compute.
angleKeys = ["hombro_fe", "hombro_abd", "codo_fe", "muneca_fe", "muneca_ud"];

% Neutral targets used for display alignment. These values should be adjusted
% only if the final documented workflow requires it.
targetNeutral = containers.Map( ...
    {'hombro_fe','hombro_abd','codo_fe','muneca_fe','muneca_ud'}, ...
    {0, 90, 0, 15, 0});

% Final manual scaling/offset parameters. Keep scale=1 and offset=0 unless a
% documented final adjustment was made during signal review.
scaleMap = containers.Map(angleKeys, [1, 1, 1, 1, 0.5]);
offsetMap = containers.Map(angleKeys, [0, 0, 0, 0, 0]);

% Participant-specific mode. Use direct_resultant for P09-P10 if available.
if ismember(participantID, ["P09", "P10"])
    defaultMode = "direct_resultant";
else
    defaultMode = "axis_offset";
end

%% ================= COMPUTE ISEN ANGLES =================
results = struct();
figure('Name', participantID + " corrected iSen patterns", 'Color', 'w', 'Position', [100 80 1000 720]);
tiledlayout(numel(angleKeys), 1, 'TileSpacing', 'compact');

for k = 1:numel(angleKeys)
    key = angleKeys(k);

    options = struct();
    options.mode = defaultMode;
    options.fc = 6;
    options.order = 4;
    options.neutralWindow = [0.2 1.0];
    options.analysisWindow = [];
    options.targetNeutral = targetNeutral(char(key));
    options.scale = scaleMap(char(key));
    options.offset = offsetMap(char(key));
    options.pairBase = "";        % Optional: set exact pair base if automatic selection is not adequate.
    options.directColumn = "";    % Optional: required if direct resultant column cannot be auto-detected.
    options.invertSign = false;

    try
        r = compute_isen_angle_from_csv(rawCsvFile, key, options);
        results.(key) = r;

        nexttile;
        plot(r.time, r.angle, 'LineWidth', 1.4);
        grid on;
        ylabel(strrep(key, '_', '\_'));
        title(sprintf('%s | axis/column: %s', key, r.axisUsed), 'Interpreter', 'none');
    catch ME
        warning('Could not process %s: %s', key, ME.message);
    end
end
xlabel('Time (s)');
exportgraphics(gcf, fullfile(outputFolder, participantID + "_corrected_isen_patterns.png"), 'Resolution', 300);

%% ================= SAVE RESULTS =================
angleTable = table();
for k = 1:numel(angleKeys)
    key = angleKeys(k);
    if isfield(results, key)
        r = results.(key);
        temp = table(r.time(:), r.angle(:), repmat(key, numel(r.time), 1), ...
            'VariableNames', {'Time_s','Angle_deg','AngleKey'});
        angleTable = [angleTable; temp]; %#ok<AGROW>
    end
end
writetable(angleTable, fullfile(outputFolder, participantID + "_corrected_isen_angles.csv"));
fprintf('Corrected iSen angle table saved for %s.\n', participantID);
