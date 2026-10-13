"""Embed a successfully built SuperTuxKart 1.5 Android source tree."""
from pathlib import Path
import os
import shutil
import subprocess
ROOT=Path(__file__).resolve().parents[1]
project=Path(os.environ['JOYORBIT_STK_SOURCE']).resolve()/'android'
module=ROOT/'build/stk-embedded';module.mkdir(parents=True,exist_ok=True)
java=module/'java'
shutil.copytree(project/'src/main/java',java,dirs_exist_ok=True)
activity=java/'SuperTuxKartActivity.java'
text=activity.read_text()
text=text.replace('public class SuperTuxKartActivity extends SDLActivity\n{', '''public class SuperTuxKartActivity extends SDLActivity
{
    private boolean joySelectDown;
    private boolean joyStartDown;
    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        if (!hasFocus) { joySelectDown = false; joyStartDown = false; }
        super.onWindowFocusChanged(hasFocus);
    }
    @Override
    public boolean dispatchKeyEvent(KeyEvent event) {
        if (event.getKeyCode() == KeyEvent.KEYCODE_BUTTON_SELECT)
            joySelectDown = event.getAction() == KeyEvent.ACTION_DOWN;
        if (event.getKeyCode() == KeyEvent.KEYCODE_BUTTON_START)
            joyStartDown = event.getAction() == KeyEvent.ACTION_DOWN;
        if (joySelectDown && joyStartDown && event.getAction() == KeyEvent.ACTION_DOWN) {
            SDLActivity.nativeSendQuit();
            return true;
        }
        if (event.getKeyCode() == KeyEvent.KEYCODE_BACK &&
            event.getAction() == KeyEvent.ACTION_DOWN && event.isLongPress()) {
            SDLActivity.nativeSendQuit();
            return true;
        }
        return super.dispatchKeyEvent(event);
    }
''',1)
activity.write_text(text)
engine=ROOT/'.sources/retroarch/pkg/android/phoenix'
for name in ('gradlew','gradlew.bat'):shutil.copy2(engine/name,module/name)
shutil.copytree(engine/'gradle',module/'gradle',dirs_exist_ok=True)
(module/'local.properties').write_text('sdk.dir='+os.environ['ANDROID_SDK_ROOT']+'\n')
(module/'AndroidManifest.xml').write_text('''<manifest xmlns:android="http://schemas.android.com/apk/res/android"><application>
<activity android:name="io.precisiondata.joyorbit.kart.SuperTuxKartActivity" android:exported="true" android:process=":kart" android:launchMode="singleInstance" android:enableOnBackInvokedCallback="false" android:screenOrientation="sensorLandscape" android:configChanges="keyboard|keyboardHidden|navigation|orientation|screenLayout|screenSize|uiMode" android:theme="@style/Theme.STKSplashScreen"/>
</application><uses-permission android:name="android.permission.VIBRATE"/></manifest>''')
(module/'build.gradle').write_text('''buildscript { repositories { google(); mavenCentral() }; dependencies { classpath 'com.android.tools.build:gradle:9.1.0' } }
repositories { google(); mavenCentral() }
apply plugin: 'com.android.library'
dependencies { implementation 'org.minidns:minidns-hla:0.3.3' }
android {
 namespace "io.precisiondata.joyorbit.kart"
 compileSdkVersion 36
 defaultConfig { minSdkVersion 23 }
 buildFeatures { buildConfig true }
 packagingOptions { jniLibs { useLegacyPackaging = true } }
 sourceSets { main {
 manifest.srcFile 'AndroidManifest.xml'
java.srcDirs = ['''+repr(str(java))+''']
 res.srcDirs = ['''+repr(str(project/'res'))+''']
 assets.srcDirs = ['''+repr(str(project/'assets'))+''']
 jniLibs.srcDirs = ['''+repr(str(project/'build/intermediates/stripped_native_libs/debug/stripDebugDebugSymbols/out/lib'))+''']
 } }
}
''')
subprocess.run(['sh',str(module/'gradlew'),'-p',str(module),'assembleDebug','--no-daemon'],check=True)
output=ROOT/'build/android-apk/libs';output.mkdir(parents=True,exist_ok=True)
shutil.copy2(module/'build/outputs/aar/stk-embedded-debug.aar',output/'joyorbit-kart.aar')
metadata=ROOT/'build/android/src/app/android/assets/joyorbit/library/stk.metadata.pegasus.txt'
metadata.write_text(metadata.read_text().replace('org.supertuxkart.stk/org.supertuxkart.stk.SuperTuxKartActivity','io.precisiondata.joyorbit/io.precisiondata.joyorbit.kart.SuperTuxKartActivity'))
print('Kart embedded; now run scripts/package-android.py')
