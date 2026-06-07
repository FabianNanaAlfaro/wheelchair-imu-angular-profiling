%% PATRONES_FINAL_clean.m
% Publication-style plots and summary tables for wheelchair IMU angular profiles.
%
% Purpose
% -------
% This script reads finalized participant-level angle files and generates:
%   1) participant-level angular profile figures,
%   2) cohort-level boxplots,
%   3) descriptive summary tables,
%   4) optional correlation matrices.
%
% Notes
% -----
% - Inputs should be de-identified and use participant codes such as P01-P10.
% - The expected columns are:
%       Porcentaje, Hombro_FE, Hombro_Abd, Codo_FE, Muneca_FE, Muneca_UD
% - Variables are device-defined IMU angular descriptors, not anatomically
%   calibrated joint angles.

clear; clc; close all;

%% ================= USER SETTINGS =================
inputFolder  = fullfile(pwd, '..', 'data');       % Edit if needed
outputFolder = fullfile(pwd, '..', 'outputs');    % Figures and tables are saved here
if ~exist(outputFolder, 'dir'), mkdir(outputFolder); end

% Accept both XLSX and CSV finalized participant profiles.
fileList = [dir(fullfile(inputFolder, '*.xlsx')); dir(fullfile(inputFolder, '*.csv'))];
fileList = fileList(~startsWith({fileList.name}, '~$'));

% Expected device-defined angular descriptors.
angleVars = {'Hombro_FE','Hombro_Abd','Codo_FE','Muneca_FE','Muneca_UD'};
prettyNames = containers.Map(angleVars, { ...
    'Shoulder flexion-extension', ...
    'Shoulder abduction-adduction', ...
    'Elbow flexion-extension', ...
    'Wrist flexion-extension', ...
    'Wrist radioulnar deviation'});

participantLabels = strings(numel(fileList),1);
allROM = table();
profileData = struct();

%% ================= READ FINALIZED ANGLE FILES =================
for i = 1:numel(fileList)
    filePath = fullfile(fileList(i).folder, fileList(i).name);
    [~, baseName, ext] = fileparts(filePath);
    participantID = standardizeParticipantLabel(baseName, i);
    participantLabels(i) = participantID;

    fprintf('Reading %s as %s\n', fileList(i).name, participantID);

    if strcmpi(ext, '.csv')
        T = readtable(filePath, 'VariableNamingRule', 'preserve');
    else
        opts = detectImportOptions(filePath, 'VariableNamingRule', 'preserve');
        T = readtable(filePath, opts);
    end

    if ~ismember('Porcentaje', T.Properties.VariableNames)
        warning('%s does not contain Porcentaje. File skipped.', fileList(i).name);
        continue;
    end

    profileData.(participantID).table = T;

    row = table(string(participantID), 'VariableNames', {'Participant'});
    for v = 1:numel(angleVars)
        varName = angleVars{v};
        if ismember(varName, T.Properties.VariableNames)
            y = T.(varName);
            row.(varName) = max(y, [], 'omitnan') - min(y, [], 'omitnan');
        else
            row.(varName) = NaN;
        end
    end
    allROM = [allROM; row]; %#ok<AGROW>
end

%% ================= PLOT TIME-NORMALIZED ANGULAR PROFILES =================
colors = lines(max(1, numel(participantLabels)));
lineStyles = {'-','--',':','-.'};

for v = 1:numel(angleVars)
    varName = angleVars{v};
    fig = figure('Name', varName, 'Color', 'w', 'Position', [100 80 1100 700]);
    hold on; grid on;

    for i = 1:numel(participantLabels)
        pid = participantLabels(i);
        if pid == "" || ~isfield(profileData, pid), continue; end
        T = profileData.(pid).table;
        if ~ismember(varName, T.Properties.VariableNames), continue; end

        ls = lineStyles{mod(i-1, numel(lineStyles)) + 1};
        plot(T.('Porcentaje'), T.(varName), 'LineWidth', 1.6, ...
            'LineStyle', ls, 'Color', colors(i,:), 'DisplayName', char(pid));
    end

    xlabel('Cycle percentage (%)');
    ylabel('Device-defined angular excursion (deg)');
    title(prettyNames(varName), 'Interpreter', 'none');
    legend('Location', 'eastoutside', 'Interpreter', 'none');
    set(gca, 'FontSize', 11, 'LineWidth', 1.0);
    exportgraphics(fig, fullfile(outputFolder, sprintf('%s_profiles.png', varName)), 'Resolution', 300);
end

%% ================= DESCRIPTIVE SUMMARY =================
summaryTable = summarizeROM(allROM, angleVars);
writetable(allROM, fullfile(outputFolder, 'participant_level_angular_excursions.csv'));
writetable(summaryTable, fullfile(outputFolder, 'cohort_angular_excursion_summary.csv'));
disp(summaryTable);

%% ================= BOXPLOT =================
fig = figure('Name', 'Angular excursion distribution', 'Color', 'w', 'Position', [120 100 950 520]);
boxData = allROM{:, angleVars};
boxplot(boxData, 'Labels', cellfun(@(x) prettyNames(x), angleVars, 'UniformOutput', false));
ylabel('Device-defined angular excursion (deg)');
title('Participant-level angular-excursion distribution');
grid on;
set(gca, 'FontSize', 10, 'LineWidth', 1.0);
exportgraphics(fig, fullfile(outputFolder, 'angular_excursion_boxplot.png'), 'Resolution', 300);

%% ================= EXPLORATORY CORRELATION MATRIX =================
R = corr(boxData, 'Type', 'Spearman', 'Rows', 'pairwise');
fig = figure('Name', 'Exploratory Spearman correlation matrix', 'Color', 'w', 'Position', [200 100 650 560]);
imagesc(R); axis image; colorbar; caxis([-1 1]);
set(gca, 'XTick', 1:numel(angleVars), 'XTickLabel', angleVars, ...
         'YTick', 1:numel(angleVars), 'YTickLabel', angleVars, ...
         'XTickLabelRotation', 45, 'FontSize', 10);
title('Exploratory Spearman correlation matrix');
for r = 1:size(R,1)
    for c = 1:size(R,2)
        text(c, r, sprintf('%.2f', R(r,c)), 'HorizontalAlignment', 'center', 'Color', 'k');
    end
end
exportgraphics(fig, fullfile(outputFolder, 'exploratory_correlation_matrix.png'), 'Resolution', 300);

%% ================= LOCAL FUNCTIONS =================
function label = standardizeParticipantLabel(baseName, idx)
    token = regexp(baseName, '(P\d{1,2}|Participant[_\s-]?\d{1,2})', 'match', 'once', 'ignorecase');
    if isempty(token)
        label = sprintf('P%02d', idx);
    else
        n = regexp(token, '\d+', 'match', 'once');
        label = sprintf('P%02d', str2double(n));
    end
end

function S = summarizeROM(T, vars)
    names = strings(numel(vars),1);
    meanVal = nan(numel(vars),1);
    sdVal = nan(numel(vars),1);
    medianVal = nan(numel(vars),1);
    minVal = nan(numel(vars),1);
    maxVal = nan(numel(vars),1);

    for k = 1:numel(vars)
        x = T.(vars{k});
        names(k) = string(vars{k});
        meanVal(k) = mean(x, 'omitnan');
        sdVal(k) = std(x, 'omitnan');
        medianVal(k) = median(x, 'omitnan');
        minVal(k) = min(x, [], 'omitnan');
        maxVal(k) = max(x, [], 'omitnan');
    end

    S = table(names, meanVal, sdVal, medianVal, minVal, maxVal, ...
        'VariableNames', {'Variable','Mean_deg','SD_deg','Median_deg','Min_deg','Max_deg'});
end
