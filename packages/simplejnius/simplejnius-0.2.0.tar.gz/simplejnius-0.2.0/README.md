# SimpleJnius

Access third party Android Java libraries in Python

## Installation
```shell
# for code completion
pip install simplejnius

# For buildozer android
requirements=simplejnius

# Optionally add java third-party sdk if actually imported in your python code
android.gradle_dependencies=com.google.guava:guava:32.0.1-android,
  org.reactivestreams:reactive-streams:1.0.4
```