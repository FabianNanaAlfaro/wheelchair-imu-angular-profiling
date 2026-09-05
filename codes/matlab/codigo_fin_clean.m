%% codigo_fin_clean.m
% iSen pattern extraction workflow.
%
% Purpose
% -------
% This script computes device-defined iSen angular descriptors for
% propulsion-pattern inspection using component selection and neutral-window
% alignment from compute_isen_angle_from_csv.m.
%
% Mode rule
% ---------
% Use 'axis_offset' when the export contains the component pair used by the
% descriptor. Use 'direct_resultant' only when the export already contains a
% validated resultant angle column. Keep that choice in the manifest/log of
% the local run.
%
% Pattern windows can be reviewed against the iSen signals before a local
% summary is produced.

clear; clc; close all;

%% ================= USER SETTINGS =================
scriptFolder = fileparts(mfilename('fullpath'));
repoRoot = fullfile(scriptFolder, '..', '..');
trialID = "DEMO";
rawCsvFile = fullfile(repoRoot, 'examples', 'synthetic', 'imu_trial.csv');  % Replace locally.
outputFolder = fullfile(repoRoot, 'outputs', 'isen_patterns');
if ~exist(outputFolder, 'dir'), mkdir(outputFolder); end

% Descriptors to compute.
angleKeys = ["hombro_fe", "hombro_abd", "codo_fe", "muneca_fe", "muneca_ud"];

% Neutral targets used for display alignment. These values should be adjusted
% only when the documented local workflow requires it.
targetNeutral = containers.Map( ...
    {'hombro_fe','hombro_abd','codo_fe','muneca_fe','muneca_ud'}, ...
    {0, 90, 0, 15, 0});

% Manual scaling/offset parameters. Keep scale=1 and offset=0 unless a
% documented local adjustment is required.
scaleMap = containers.Map(angleKeys, [1, 1, 1, 1, 0.5]);
offsetMap = containers.Map(angleKeys, [0, 0, 0, 0, 0]);

% Public demo uses the component + neutral-window workflow.
defaultMode = "axis_offset";

%% ================= COMPUTE ISEN ANGLES =================
results = struct();
figure('Name', trialID + " iSen patterns", 'Color', 'w', 'Position', [100 80 1000 720]);
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
exportgraphics(gcf, fullfile(outputFolder, trialID + "_isen_patterns.png"), 'Resolution', 300);

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
writetable(angleTable, fullfile(outputFolder, trialID + "_isen_angles.csv"));
fprintf('iSen angle table saved for %s.\n', trialID);
