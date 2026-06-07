%% automatizacion_clean.m
% Legacy/support utility for Kinovea coordinate processing.
%
% Purpose
% -------
% This script provides a cleaned reference workflow for reading Kinovea Excel
% exports, normalizing coordinate fields, and generating support trajectories.
% It is not the primary source of manuscript angular variables. It can be used
% to support visual inspection, cycle-boundary confirmation, and qualitative
% pattern review.

clear; clc; close all;

%% ================= USER SETTINGS =================
sagittalFile = "../data/kinovea/P01_sagittal.xlsx";  % Edit locally.
frontalFile  = "../data/kinovea/P01_frontal.xlsx";   % Edit locally.
outputFolder = fullfile(pwd, '..', 'outputs', 'kinovea_support');
if ~exist(outputFolder, 'dir'), mkdir(outputFolder); end

%% ================= READ KINOVEA EXPORTS =================
sag = readKinoveaTable(sagittalFile);
fro = readKinoveaTable(frontalFile);

%% ================= NORMALIZE COORDINATES =================
% Coordinate normalization is used only for visual comparison and quality
% control. It should not be interpreted as calibrated videogrammetric analysis.
sagNorm = normalizeCoordinateTable(sag);
froNorm = normalizeCoordinateTable(fro);

writetable(sagNorm, fullfile(outputFolder, 'sagittal_coordinates_normalized.csv'));
writetable(froNorm, fullfile(outputFolder, 'frontal_coordinates_normalized.csv'));

fprintf('Kinovea support files were processed and saved in: %s\n', outputFolder);

%% ================= LOCAL FUNCTIONS =================
function T = readKinoveaTable(filePath)
    if ~isfile(filePath)
        warning('File not found: %s. Returning empty table.', filePath);
        T = table();
        return;
    end
    T = readtable(filePath, 'VariableNamingRule', 'preserve');
end

function Tnorm = normalizeCoordinateTable(T)
    Tnorm = T;
    if isempty(T), return; end
    numericCols = T.Properties.VariableNames(varfun(@isnumeric, T, 'OutputFormat', 'uniform'));
    for i = 1:numel(numericCols)
        col = numericCols{i};
        x = T.(col);
        if all(~isfinite(x)), continue; end
        Tnorm.(col) = (x - min(x, [], 'omitnan')) ./ range(x, 'omitnan');
    end
end
