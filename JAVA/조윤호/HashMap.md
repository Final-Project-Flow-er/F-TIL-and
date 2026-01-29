# HashMap

# 1. HashMap이란?
> Key(키) – Value(값) 형태로 데이터를 저장하는 자료구조

---

# 2. 선언
```
Map<K, V>
```
키와 값의 형태로 선언을 하게 되고, 예시로 들면
```java
Map<String, Integer> map = new HashMap<>();
```
키 값이 String형이고, 값이 Integer형이 된다.

---

# 3. HashMap메소드

## 3.1. put()
```
Map<String, Integer> map = new HashMap<>();

map.put(1,"사과");
map.put(2,"바나나");
map.put(3,"포도");
```
키와 값을 넣어 map에 저장
* 키가 이미 존재하면 값을 덮어쓴다.

## 3.2. get()
```
System.out.print(map.get(1));
// 사과
```
get을 사용하여 키값을 넣으면 키에 해당하는 값을 꺼내온다.
* 키가 없으면 null 반환한다.

### 만약 키가 없어도 값을 반환하고 싶다면,
```java
String str = map.getOrDefault(4, "apple");
System.out.print(str);
// apple
```
4라는 키가 존재하지 않을 경우 "apple" 반환

## 3.3. containsKey()
```
boolean tr = map.containsKey(2);
// tr = true
```
containsKey()를 사용하여 해당 Key의 존재 여부를 알 수 있으며 존재하면 True, 존재하지 않으면 false를 반환한다.

---

# 4. 반복문에 사용하고 싶을 때
```
Map<String, Integer> map = new HashMap<>();

map.put(1,"사과");
map.put(2,"바나나");
map.put(3,"포도");
```

## 4.1. keySet()

```
for(Integer key : map.keySet()){
    System.out.print(key + " ");
}

// 1 2 3
```

keySet()은 키 집합을 반환한다.

## 4.2. values()
```
for(String value : map.values()){
    System.out.print(value + " ");
}

// 사과 바나나 포도
```

values()는 값 집합을 반환한다.

## 4.3. entrySet()
```
for(Map.Entry<String, Integer> entry : map.entrySet()){
    System.out.println(entry.getKey() + " " + entry.getValue());
    }
/*
1 사과
2 바나나
3 포도
*/
```

Map.Entry 객체의 집합을 반환합니다. 키와 값을 꺼낼 수 있다.


