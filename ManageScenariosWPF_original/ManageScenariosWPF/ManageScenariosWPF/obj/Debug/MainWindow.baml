   M S B A M L   `   `   `  ����O  Kmscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e0891&clr-namespace:System;assembly=mscorlibSystem  5       ManageScenariosWPF#   ManageScenariosWPF.MainWindow   5   	   R NWindowsBase, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35W SPresentationCore, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35\ XPresentationFramework, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35D 9http://schemas.microsoft.com/winfx/2006/xaml/presentation    5      R NSystem.Xaml, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089:x,http://schemas.microsoft.com/winfx/2006/xaml     5      @basics-http://schemas.microsoft.com/wpf/2008/toolkit     5      6sys&clr-namespace:System;assembly=mscorlib     5      ` \ESRI.ArcGIS.Client.Local, Version=10.2.5.0, Culture=neutral, PublicKeyToken=29c6dd6e8553d944b ^ESRI.ArcGIS.Client.Toolkit, Version=10.2.5.0, Culture=neutral, PublicKeyToken=29c6dd6e8553d944n jESRI.ArcGIS.Client.Toolkit.DataSources, Version=10.2.5.0, Culture=neutral, PublicKeyToken=29c6dd6e8553d944Z	 VESRI.ArcGIS.Client, Version=10.2.5.0, Culture=neutral, PublicKeyToken=29c6dd6e8553d944;esri*http://schemas.esri.com/arcgis/client/2009    	 5      $��675.6��5   1   $
��1100��6@     � Title$&   RPS OilMap Scenario Manager: ES2��5   C   .��5      � 
�������$��
0,10,0,0.2q�6    � 	Resources 5   
   ��%    5	       � ColumnDefinitions 5
   
   �� 5      $	��400 �6   �� 5      �� 5      $	��0.8 �6   �� 5      $��333.6 �6   .+�5   
   0  *ESRI.ArcGIS.Client.Toolkit.FeatureDataGrid  -   5          Name$ 
MyDataGrid��5   /   $��0��6   
���   � J� RenderTransformOrigin$ 0.5,0.5&�6V   $��
0,2,0,25.4q�6v   z�5      V� 5      .~�5      �� �� 5       �� AngleY$ 0.273Q�6$   �� 5      T� 5       T� Y$ 0.715Q�6)   5      5       	 ESRI.ArcGIS.Client.Map  5   
   -   5          Name$ MyMap��5      $��1��6"      IsLogoVisible .  	   
WrapAround	 . 
   UseAcceleratedDisplay
 . $��10,-22,5.2,158q�6�   $	��492��6�   $��Bottom=�6�      Layers. 5      3 	 -ESRI.ArcGIS.Client.ArcGISTiledMapServiceLayer   	 ESRI.ArcGIS.Client.Layer	   ID$ StreetMapLayer��6.   
   Url$S Mhttp://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer��5      % 	 ESRI.ArcGIS.Client.FeatureLayer  5      -   5        $ TrajectoriesLayer��5       TrajectoriesLayer��
   Url$h bhttp://services.arcgis.com/7DPiBDyCvtJlGoFZ/arcgis/rest/services/ASA_OilMap_Models/FeatureServer/0��5   )      DisableClientCaching .    Mode$ Snapshot=�5    )      AutoSave .     OnDemandCacheSize$ 0��5"   )      	OutFieldsC 	 =ESRI.ArcGIS.Client.Tasks.OutFields+StringToOutFieldsConverter$ * 5#   )   5%      5&      �� 5'   
   -   5         ��Name$ ResponseTextBlock��5'      $��3��6-   $-��'Manage OilMap Scenarios:  Status Window��6=    �� TextAlignment$
 Left=�5(       �� TextWrapping$
 Wrap=�6"   
���   �$
��Left=�6I   $ �� HorizontalScrollBarVisibility$
 Auto=�6d   " �� VerticalScrollBarVisibility$
 Auto=�6�   $	��314��6�   $��10,10,0,10.4q�6�   .��6�   5)      � 5*   
   .+�5+      �� -   5         ��Name$ DeleteScenarioButton��5+      $��Delete Scenario(s)��63    � ToolTip$s mSelect scenario(s) in the data grid.  Click 'Delete Scenarios' to delete all data related to the scenario(s).��6s   $��525,512,-236,93.2q�6�    K� ZIndex$ 1��6  $ 0.5,0.5&�6  $
��Left=�67  $	��111��6R  5,      5-      5.      