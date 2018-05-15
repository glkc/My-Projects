C1Sx = [1537, 1566, 1598, 1639, 1681, 1672];
C1Sy = [1449, 1443, 1433, 1444, 1451, 1491];
C1Gx = [50,   76,  834, 1804, 2978, 3142];
C1Gy = [1395,  141,   74,   86,  242, 1324];

C2Sx = [28, 3116, 66, 3084, 110, 103];
C2Sy = [163, 342, 610, 849, 1127, 1384];
C2Gx = [3139, 66, 3089, 124, 3079, 1568];
C2Gy = [216, 413, 629, 935, 1127, 1412];

C3Sx = [ 973, 1353, 1304, 1187];
C3Sy = [ 691,  540, 1012, 1156];
C3Gx = [1032, 1409, 1332, 1071];
C3Gy = [684, 586, 1011, 297];

C4Sx = [1838, 1531, 1390];
C4Sy = [1393, 1384, 1523];
C4Gx = [348, 258, 58];
C4Gy = [43, 116, 178];

C5Sx = [1515, 1730, 3098, 21, 3070, 48];
C5Sy = [64, 1493, 764, 932, 104, 63];
C5Gx = [1407, 1702, 90, 3058, 96, 3084];
C5Gy = [1459, 70, 751, 876, 1457, 1435];

C6Sx = [670, 1340, 1360, 1824, 1677, 1317];
C6Sy = [898, 456, 1022, 460, 851, 238];
C6Gx = [1463, 749, 826, 1340, 1177, 910];
C6Gy = [708, 531, 516, 1062, 917, 1064];

dinfo = dir('RunsData/Trial-5/*/*/*/UAV_Path');
for K = 1 : length(dinfo)
  pathData = load(dinfo(K).folder+"\"+dinfo(K).name);  %just the name
  clf
  hold on
  if ~isempty(strfind(dinfo(K).folder, "Case-1"))
      for j  = 1:6
          plot(C1Sx(j), C1Sy(j), 'r*')
          line([C1Sx(j), C1Gx(j)],[C1Sy(j), C1Gy(j)],'Color', 'r')
      end
  end
  if ~isempty(strfind(dinfo(K).folder, "Case-2"))
      for j  = 1:6
          plot(C2Sx(j), C2Sy(j), 'r*')
          line([C2Sx(j), C2Gx(j)],[C2Sy(j), C2Gy(j)],'Color', 'r')
      end
  end
  if ~isempty(strfind(dinfo(K).folder, "Case-3"))
      for j  = 1:4
          plot(C3Sx(j), C3Sy(j), 'r*')
          line([C3Sx(j), C3Gx(j)],[C3Sy(j), C3Gy(j)],'Color', 'r')
      end
  end
  if ~isempty(strfind(dinfo(K).folder, "Case-4"))
      for j  = 1:3
          plot(C4Sx(j), C4Sy(j), 'r*')
          line([C4Sx(j), C4Gx(j)],[C4Sy(j), C4Gy(j)],'Color', 'r')
      end
  end
  if ~isempty(strfind(dinfo(K).folder, "Case-5"))
      for j  = 1:6
          plot(C5Sx(j), C5Sy(j), 'r*')
          line([C5Sx(j), C5Gx(j)],[C5Sy(j), C5Gy(j)],'Color', 'r')
      end
  end
  if ~isempty(strfind(dinfo(K).folder, "Case-6"))
      for j  = 1:6
          plot(C6Sx(j), C6Sy(j), 'r*')
          line([C6Sx(j), C6Gx(j)],[C6Sy(j), C6Gy(j)],'Color', 'r')
      end
  end
  pathData = pathData(:, 1:2);
  plt = plot(pathData(:,1), pathData(:,2), '--');
  set(gca, 'YDir', 'reverse');
  xlim([0 3200])
  ylim([0 1600])
  hold off
  fileName = char(dinfo(K).folder+"\UAVPath"+K+".jpg");
  saveas(plt, fileName,'jpeg'); 
end
