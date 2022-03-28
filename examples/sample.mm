<map version="freeplane 1.7.0">
<!--To view this file, download free mind mapping software Freeplane from http://freeplane.sourceforge.net -->
<node TEXT="Project Title" FOLDED="false" ID="ID_649210365" CREATED="1648453170076" MODIFIED="1648453243242" STYLE="oval">
<font SIZE="18"/>
<hook NAME="MapStyle">
    <properties edgeColorConfiguration="#808080ff,#ff0000ff,#0000ffff,#00ff00ff,#ff00ffff,#00ffffff,#7c0000ff,#00007cff,#007c00ff,#7c007cff,#007c7cff,#7c7c00ff" fit_to_viewport="false" show_note_icons="true"/>

<map_styles>
<stylenode LOCALIZED_TEXT="styles.root_node" STYLE="oval" UNIFORM_SHAPE="true" VGAP_QUANTITY="24.0 pt">
<font SIZE="24"/>
<stylenode LOCALIZED_TEXT="styles.predefined" POSITION="right" STYLE="bubble">
<stylenode LOCALIZED_TEXT="default" ICON_SIZE="12.0 pt" COLOR="#000000" STYLE="fork">
<font NAME="SansSerif" SIZE="10" BOLD="false" ITALIC="false"/>
</stylenode>
<stylenode LOCALIZED_TEXT="defaultstyle.details"/>
<stylenode LOCALIZED_TEXT="defaultstyle.attributes">
<font SIZE="9"/>
</stylenode>
<stylenode LOCALIZED_TEXT="defaultstyle.note" COLOR="#000000" BACKGROUND_COLOR="#ffffff" TEXT_ALIGN="LEFT"/>
<stylenode LOCALIZED_TEXT="defaultstyle.floating">
<edge STYLE="hide_edge"/>
<cloud COLOR="#f0f0f0" SHAPE="ROUND_RECT"/>
</stylenode>
</stylenode>
<stylenode LOCALIZED_TEXT="styles.user-defined" POSITION="right" STYLE="bubble">
<stylenode LOCALIZED_TEXT="styles.topic" COLOR="#18898b" STYLE="fork">
<font NAME="Liberation Sans" SIZE="10" BOLD="true"/>
</stylenode>
<stylenode LOCALIZED_TEXT="styles.subtopic" COLOR="#cc3300" STYLE="fork">
<font NAME="Liberation Sans" SIZE="10" BOLD="true"/>
</stylenode>
<stylenode LOCALIZED_TEXT="styles.subsubtopic" COLOR="#669900">
<font NAME="Liberation Sans" SIZE="10" BOLD="true"/>
</stylenode>
<stylenode LOCALIZED_TEXT="styles.important">
<icon BUILTIN="yes"/>
</stylenode>
</stylenode>
<stylenode LOCALIZED_TEXT="styles.AutomaticLayout" POSITION="right" STYLE="bubble">
<stylenode LOCALIZED_TEXT="AutomaticLayout.level.root" COLOR="#000000" STYLE="oval" SHAPE_HORIZONTAL_MARGIN="10.0 pt" SHAPE_VERTICAL_MARGIN="10.0 pt">
<font SIZE="18"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,1" COLOR="#0033ff">
<font SIZE="16"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,2" COLOR="#00b439">
<font SIZE="14"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,3" COLOR="#990000">
<font SIZE="12"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,4" COLOR="#111111">
<font SIZE="10"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,5"/>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,6"/>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,7"/>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,8"/>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,9"/>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,10"/>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,11"/>
</stylenode>
</stylenode>
</map_styles>
</hook>
<hook NAME="AutomaticEdgeColor" COUNTER="2" RULE="ON_BRANCH_CREATION"/>
<hook NAME="accessories/plugins/AutomaticLayout.properties" VALUE="ALL"/>
<node TEXT="Epic Task (level 1)" POSITION="right" ID="ID_1217178176" CREATED="1648453228225" MODIFIED="1648453234541">
<edge COLOR="#ff0000"/>
<node TEXT="Task (level 2)" ID="ID_1322682499" CREATED="1648453245568" MODIFIED="1648453251140">
<node TEXT="Subtask (level 3)" ID="ID_275798023" CREATED="1648453258907" MODIFIED="1648453268532"/>
</node>
</node>
<node TEXT="Epic Task (with note as JIRA Description)" POSITION="right" ID="ID_1924064848" CREATED="1648453271481" MODIFIED="1648453351243">
<edge COLOR="#0000ff"/>
<richcontent TYPE="NOTE">

<html>
  <head>
    
  </head>
  <body>
    <p>
      h1. This is a test
    </p>
    <p>
      ---
    </p>
    <p>
      * Bullet 1
    </p>
    <p>
      ** Bullet 2
    </p>
    <p>
      *** Bullet 3
    </p>
    <p>
      ** Foo
    </p>
    <p>
      ** Bar
    </p>
    <p>
      * Baz
    </p>
  </body>
</html>

</richcontent>
<node TEXT="Task w/ Note" ID="ID_193849018" CREATED="1648453357018" MODIFIED="1648453391596"><richcontent TYPE="NOTE">

<html>
  <head>
    
  </head>
  <body>
    <p>
      Hello World
    </p>
    <p>
      {code}
    </p>
    <p>
      #!/usr/bin/env bash
    </p>
    <p>
      echo &quot;hello world&quot;
    </p>
    <p>
      {code}
    </p>
  </body>
</html>

</richcontent>
<node TEXT="Subtask" ID="ID_1801125028" CREATED="1648453393586" MODIFIED="1648453401337">
<node TEXT="Here is a mindmap that will be presented as bullet points" ID="ID_1769698850" CREATED="1648453402640" MODIFIED="1648453421329">
<node TEXT="Level2" ID="ID_1414452373" CREATED="1648453491146" MODIFIED="1648453493921">
<node TEXT="Level 3" ID="ID_109739138" CREATED="1648453495388" MODIFIED="1648453497986"/>
</node>
</node>
<node TEXT="foo" ID="ID_1873511195" CREATED="1648453422065" MODIFIED="1648453424029"/>
<node TEXT="bar" ID="ID_1898890088" CREATED="1648453426092" MODIFIED="1648453427041"/>
<node TEXT="baz" ID="ID_1831329226" CREATED="1648453427423" MODIFIED="1648453428585">
<node TEXT="Another level" ID="ID_1130534038" CREATED="1648453430097" MODIFIED="1648453433950"/>
<node TEXT="This one has multiple lines and will show up as code&#xa;This&#xa;is&#xa;a&#xa;test&#xa;hello world" ID="ID_1118672783" CREATED="1648453434627" MODIFIED="1648453479115">
<node TEXT="next level" ID="ID_470342437" CREATED="1648453482759" MODIFIED="1648453484869"/>
</node>
</node>
</node>
</node>
</node>
</node>
</map>
