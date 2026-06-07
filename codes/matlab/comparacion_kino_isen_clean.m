%% comparacion_kino_isen_clean.m
% Kinovea-vs-iSen visual quality-control comparison.
%
% Purpose
% -------
% This script overlays Kinovea/video-derived support trajectories with corrected
% iSen angular descriptors. It is intended for quality-control review only.
% The quantitative angular variables reported in the manuscript come from the
% iSen outputs, not from Kinovea.
%
% Correction implemented
% ----------------------
% Earlier exploratory comparisons estimated iSen angles using atan2(X,Y). The
% final comparison below uses compute_isen_angle_from_csv.m, which follows the
% corrected iSen angle workflow used for the final patterns.

clear; clc; close all;

%% ================= USER SETTINGS =================
participantID = "P10";
isenCsvFile = "../data/raw_isen/P10.csv";           % Edit locally.
kinoveaSagittalFile = "../data/kinovea/P10_sagittal.xlsx"; % Optional support file.
kinoveaFrontalFile  = "../data/kinovea/P10_frontal.xlsx";  % Optional support file.
outputFolder = fullfile(pwd, '..', 'outputs', 'kinovea_isen_qc');
if ~exist(outputFolder, 'dir'), mkdir(outputFolder); end

angleKey = "codo_fe";     % Change to desired descriptor.

% P09-P10 can use direct resultant mode if the resultant angle exists.
options = struct();
options.mode = "direct_resultant";
options.fc = 6;
options.order = 4;
options.neutralWindow = [0.2 1.0];
options.targetNeutral = 0;
options.scale = 1;
options.offset = 0;
options.directColumn = "";

%% ================= CORRECTED ISEN ANGLE =================
isenResult = compute_isen_angle_from_csv(isenCsvFile, angleKey, options);

%% ================= OPTIONAL KINOVEA SUPPORT SIGNAL =================
% The function below attempts to read a simple Kinovea coordinate export. If the
% exact columns are different, edit the column names in buildKinoveaSupportAngle.
kinovea = [];
if isfile(kinoveaSagittalFile)
    try
        kinovea = buildKinoveaSupportAngle(kinoveaSagittalFile);
    catch ME
        warning('Kinovea support angle could not be computed: %s', ME.message);
    end
end

%% ================= PLOT QC OVERLAY =================
fig = figure('Name', participantID + " Kinovea-iSen QC", 'Color', 'w', 'Position', [100 100 1000 520]);
hold on; grid on;
plot(isenResult.time, normalizeForOverlay(isenResult.angle), 'LineWidth', 1.8, 'DisplayName', 'Corrected iSen descriptor');
if ~isempty(kinovea)
    plot(kinovea.time, normalizeForOverlay(kinovea.angle), '--', 'LineWidth', 1.4, 'DisplayName', 'Kinovea support trajectory');
end
xlabel('Time (s)');
ylabel('Normalized signal for visual comparison');
title('Kinovea support vs corrected iSen pattern (visual QC only)');
legend('Location', 'best');
exportgraphics(fig, fullfile(outputFolder, participantID + "_kinovea_isen_qc.png"), 'Resolution', 300);

%% ================= LOCAL FUNCTIONS =================
function y = normalizeForOverlay(x)
    x = double(x(:));
    y = (x - mean(x, 'omitnan')) ./ std(x, 'omitnan');
end

function out = buildKinoveaSupportAngle(filePath)
    T = readtable(filePath, 'VariableNamingRule', 'preserve');
    headers = string(T.Properties.VariableNames);

    % This is a generic example. Edit these names if your Kinovea export uses
    % different coordinate labels.
    timeCol = headers(1);
    time = T.(timeCol);
    if isdatetime(time), time = seconds(time - time(1)); end
    time = double(time(:));
    time = time - time(1);

    numericCols = headers(varfun(@isnumeric, T, 'OutputFormat', 'uniform'));
    assert(numel(numericCols) >= 6, 'At least three 2D points are required.');

    % Use the first three 2D points as a generic support angle if exact landmark
    % names are not provided.
    P1 = [T.(numericCols(1)), T.(numericCols(2))];
    P2 = [T.(numericCols(3)), T.(numericCols(4))];
    P3 = [T.(numericCols(5)), T.(numericCols(6))];
    angle = angleFromThreePoints(P1, P2, P3);

    out = struct('time', time, 'angle', angle);
end

function theta = angleFromThreePoints(A, B, C)
    BA = A - B;
    BC = C - B;
    dotProd = sum(BA .* BC, 2);
    normProd = vecnorm(BA, 2, 2) .* vecnorm(BC, 2, 2);
    theta = acosd(max(min(dotProd ./ normProd, 1), -1));
end
